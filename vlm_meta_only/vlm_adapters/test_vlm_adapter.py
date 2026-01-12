import json
import os
import sys
from typing import Any, Dict

if __package__ is None:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from vlm_adapters.openai_vlm_adapter import OpenAIVLMAdapter
    from vlm_adapters.mock_vlm_adapter import MockVLMAdapter
else:
    from .openai_vlm_adapter import OpenAIVLMAdapter
    from .mock_vlm_adapter import MockVLMAdapter


def _load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def _build_adapter(cfg: Dict[str, Any]):
    provider = cfg.get("provider", "openai")
    if provider == "openai":
        return OpenAIVLMAdapter(cfg.get("openai", {}))
    if provider == "mock":
        return MockVLMAdapter(cfg.get("mock", {}))
    raise ValueError(f"Unknown provider: {provider}")


def main() -> int:
    config_path = os.environ.get("VLM_CONFIG", "vlm_adapters/config.json")
    cfg = _load_config(config_path)
    adapter = _build_adapter(cfg)
    test_cfg = cfg.get("test", {})

    image = test_cfg.get("image")
    prompt = test_cfg.get("prompt", "")
    context = test_cfg.get("context", {})
    if not image:
        print("Missing test.image in config.", file=sys.stderr)
        return 1

    obs = adapter.predict(image=image, prompt=prompt, context=context)
    print(json.dumps(obs.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
