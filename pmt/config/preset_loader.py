"""프리셋 YAML 파일 로더."""

from pathlib import Path
from typing import Any

import yaml


class PresetLoader:
    """YAML 프리셋 파일 로더."""

    def __init__(self, presets_dir: Path) -> None:
        """초기화."""
        self.presets_dir = presets_dir

    def load_all(self) -> list[dict[str, Any]]:
        """모든 프리셋 파일 로드."""
        presets: list[dict[str, Any]] = []

        if not self.presets_dir.exists():
            return presets

        for yaml_file in self.presets_dir.glob("*.yaml"):
            presets.extend(self._load_file(yaml_file))

        return presets

    def _load_file(self, file_path: Path) -> list[dict[str, Any]]:
        """단일 YAML 파일 로드."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"프리셋 파일 로드 실패 {file_path}: {e}")
            return []

