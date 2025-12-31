"""프리셋 관리자."""

from pathlib import Path
from typing import Any, Optional

from pmt.config.preset_loader import PresetLoader
from pmt.config.settings import Settings


class PresetManager:
    """프리셋 로드 및 관리."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        self.settings = settings
        self.loader = PresetLoader(settings.presets_dir)
        self._presets: list[dict[str, Any]] = []
        self._presets_by_name: dict[str, dict[str, Any]] = {}
        self._load_presets()

    def _load_presets(self) -> None:
        """프리셋 로드."""
        self._presets = self.loader.load_all()
        self._presets_by_name = {preset.get("name", ""): preset for preset in self._presets}

    def get_all_presets(self) -> list[dict[str, Any]]:
        """모든 프리셋 반환."""
        return self._presets.copy()

    def get_preset(self, preset_name: str) -> Optional[dict[str, Any]]:
        """
        프리셋 이름으로 프리셋 조회.

        Args:
            preset_name: 프리셋 이름

        Returns:
            프리셋 데이터 또는 None
        """
        return self._presets_by_name.get(preset_name)

    def reload_presets(self) -> None:
        """프리셋 재로드."""
        self._load_presets()

