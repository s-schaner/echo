import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

@dataclass
class TMU:
    """Token Memory Unit."""
    id: str
    content: str
    metadata: Dict[str, Any] | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(data: str) -> 'TMU':
        payload = json.loads(data)
        return TMU(
            id=payload.get("id", ""),
            content=payload.get("content", ""),
            metadata=payload.get("metadata"),
        )


def load_tmu(path: str | Path) -> TMU:
    """Load a TMU from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return TMU.from_json(fh.read())


def save_tmu(tmu: TMU, path: str | Path) -> None:
    """Save a TMU to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(tmu.to_json())
