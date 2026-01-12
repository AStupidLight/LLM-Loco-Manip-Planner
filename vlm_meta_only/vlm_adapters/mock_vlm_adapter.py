import json
import os
from typing import Any, Dict, Optional

from .base import SceneObservation, VLMAdapter


class MockVLMAdapter(VLMAdapter):
    name = "mock"
    version = "1.0.0"

    def __init__(self, cfg: Dict[str, Any]):
        self._cfg = cfg
        self._annotation_dir = cfg.get("annotation_dir", "data/annotations")
        self._caption_language = cfg.get("caption_language", "zh")

    def predict(
        self,
        image: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SceneObservation:
        image_id = _infer_image_id(image)
        ann_path = os.path.join(self._annotation_dir, f"{image_id}.json")
        if not os.path.exists(ann_path):
            raise FileNotFoundError(f"Annotation not found: {ann_path}")

        with open(ann_path, "r") as f:
            ann = json.load(f)

        caption = ann.get("caption")
        if not caption:
            caption = _build_caption(prompt, ann.get("objects", []), self._caption_language)

        return SceneObservation(
            image_id=ann.get("image_id", image_id),
            objects=ann.get("objects", []),
            relations=ann.get("relations", []),
            caption=caption,
            raw_text=json.dumps(ann, ensure_ascii=False),
            meta={"provider": self.name},
        )


def _infer_image_id(image: str) -> str:
    basename = os.path.basename(image)
    if "." in basename:
        return basename.rsplit(".", 1)[0]
    return basename


def _build_caption(prompt: str, objects: list, language: str) -> str:
    if language.lower().startswith("zh"):
        obj_names = [obj.get("name", "") for obj in objects if obj.get("name")]
        obj_part = "\u3001".join(obj_names) if obj_names else "\u4e00\u4e9b\u7269\u4f53"
        return (
            f"\u7528\u6237\u6307\u4ee4\u662f\uff1a{prompt}\u3002"
            f"\u6211\u770b\u5230{obj_part}\uff0c\u51c6\u5907\u5148\u5904\u7406\u6700\u8fd1\u7684\u76ee\u6807\u3002"
        )
    obj_names = [obj.get("name", "") for obj in objects if obj.get("name")]
    obj_part = ", ".join(obj_names) if obj_names else "some objects"
    return f"User task: {prompt}. I see {obj_part} and will act on the closest target."
