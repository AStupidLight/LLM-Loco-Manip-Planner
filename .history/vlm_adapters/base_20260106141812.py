import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SceneObservation:
    image_id: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    caption: str = ""
    raw_text: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "objects": self.objects,
            "relations": self.relations,
            "caption": self.caption,
            "raw_text": self.raw_text,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObservation":
        return cls(
            image_id=data.get("image_id", ""),
            objects=data.get("objects", []),
            relations=data.get("relations", []),
            caption=data.get("caption", ""),
            raw_text=data.get("raw_text", ""),
            meta=data.get("meta", {}),
        )


# 模板类：输入

class VLMAdapter(abc.ABC):
    name: str = "base"
    version: str = "0.0.0"

    @abc.abstractmethod
    def predict(
        self,
        image: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SceneObservation:
        raise NotImplementedError
