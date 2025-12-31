"""애플리케이션 설정 관리."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Settings:
    """애플리케이션 전역 설정."""

    def __init__(self) -> None:
        """설정 초기화."""
        # .env 파일 로드
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # 기본 경로 설정
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.presets_dir = self.base_dir / "presets"
        self.data_dir.mkdir(exist_ok=True)
        self.presets_dir.mkdir(exist_ok=True)

        # 거래소 인증 정보
        self.polymarket_private_key: Optional[str] = os.getenv("POLYMARKET_PRIVATE_KEY")
        self.polymarket_funder: Optional[str] = os.getenv("POLYMARKET_FUNDER")

        self.opinion_api_key: Optional[str] = os.getenv("OPINION_API_KEY")
        self.opinion_private_key: Optional[str] = os.getenv("OPINION_PRIVATE_KEY")
        self.opinion_multi_sig_addr: Optional[str] = os.getenv("OPINION_MULTI_SIG_ADDR")

        self.limitless_private_key: Optional[str] = os.getenv("LIMITLESS_PRIVATE_KEY")

        # 리스크 가드 설정
        self.dry_run_mode: bool = os.getenv("DRY_RUN_MODE", "true").lower() == "true"
        self.max_notional: float = float(os.getenv("MAX_NOTIONAL", "1000"))
        self.max_size: float = float(os.getenv("MAX_SIZE", "1000"))
        self.cache_refresh_interval: int = int(os.getenv("CACHE_REFRESH_INTERVAL", "30"))

    def get_exchange_config(self, exchange_name: str) -> dict:
        """거래소별 설정 딕셔너리 반환."""
        config: dict = {"timeout": 30}

        if exchange_name.lower() == "polymarket":
            if self.polymarket_private_key:
                config["private_key"] = self.polymarket_private_key
            if self.polymarket_funder:
                config["funder"] = self.polymarket_funder
        elif exchange_name.lower() == "opinion":
            if self.opinion_api_key:
                config["api_key"] = self.opinion_api_key
            if self.opinion_private_key:
                config["private_key"] = self.opinion_private_key
            if self.opinion_multi_sig_addr:
                config["multi_sig_addr"] = self.opinion_multi_sig_addr
        elif exchange_name.lower() == "limitless":
            if self.limitless_private_key:
                config["private_key"] = self.limitless_private_key

        return config

