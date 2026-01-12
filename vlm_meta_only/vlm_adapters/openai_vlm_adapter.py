import base64
import json
import mimetypes
import os
from typing import Any, Dict, Optional

from openai import OpenAI

from .base import SceneObservation, VLMAdapter


class OpenAIVLMAdapter(VLMAdapter):
    name = "openai"
    version = "1.0.0"

    def __init__(self, cfg: Dict[str, Any]):
        self._cfg = cfg
        api_key = cfg.get("api_key") or os.environ.get(cfg.get("api_key_env", ""))
        base_url = cfg.get("base_url")
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = cfg.get("model", "gpt-4o-mini")
        self._temperature = cfg.get("temperature", 0.0)
        self._max_tokens = cfg.get("max_tokens", 512)
        self._timeout = cfg.get("timeout", 30)
        self._caption_language = cfg.get("caption_language", "zh")

    def predict(
        self,
        image: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SceneObservation:
        image_id = _infer_image_id(image)
        image_part = _build_image_part(image)
        system_text = _build_system_prompt(self._caption_language)
        user_text = _build_user_prompt(prompt, context)

        messages = [
            {"role": "system", "content": system_text},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    image_part,
                ],
            },
        ]

        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            timeout=self._timeout,
            messages=messages,
        )
        raw_text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        usage_dict = None
        if usage is not None:
            usage_dict = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }
        parsed = _safe_parse_json(raw_text)
        obs = SceneObservation(
            image_id=parsed.get("image_id", image_id),
            objects=parsed.get("objects", []),
            relations=parsed.get("relations", []),
            caption=parsed.get("caption", ""),
            raw_text=raw_text,
            meta={
                "model": self._model,
                "provider": self.name,
                "usage": usage_dict,
            },
        )
        return obs


def _infer_image_id(image: str) -> str:
    basename = os.path.basename(image)
    if "." in basename:
        return basename.rsplit(".", 1)[0]
    return basename


def _build_image_part(image: str) -> Dict[str, Any]:
    if image.startswith("http://") or image.startswith("https://"):
        return {"type": "image_url", "image_url": {"url": image}}

    if not os.path.exists(image):
        raise FileNotFoundError(f"Image not found: {image}")

    mime_type, _ = mimetypes.guess_type(image)
    if mime_type is None:
        mime_type = "image/png"

    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded}"
    return {"type": "image_url", "image_url": {"url": data_url}}


def _build_system_prompt(caption_language: str) -> str:
    return (
        "You are a visual perception module. "
        "Return ONLY valid JSON with keys: "
        "image_id, objects, relations, caption. "
        "Objects is a list of {name, attributes?, position?, confidence?}. "
        "Relations is a list of {subj, rel, obj, confidence?}. "
        "Caption must be a short natural-language summary that includes: "
        "(1) understanding of the user task, (2) key objects and locations, "
        "(3) immediate action intent. "
        f"Caption language: {caption_language}."
    )


def _build_user_prompt(prompt: str, context: Optional[Dict[str, Any]]) -> str:
    context_json = json.dumps(context or {}, ensure_ascii=True)
    return (
        "User instruction:\n"
        f"{prompt}\n\n"
        "Context (JSON):\n"
        f"{context_json}\n\n"
        "Return JSON only."
    )


def _safe_parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return {}
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
