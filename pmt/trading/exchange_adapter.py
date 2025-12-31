"""dr-manhattan 거래소 어댑터."""

from typing import Any, Optional

import dr_manhattan
from dr_manhattan.base.exchange import Exchange

from pmt.config.settings import Settings


class ExchangeAdapter:
    """dr-manhattan 거래소를 PMT에 맞게 래핑."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        self.settings = settings
        self._exchanges: dict[str, Exchange] = {}

    def get_exchange(self, exchange_name: str) -> Optional[Exchange]:
        """거래소 인스턴스 가져오기 (캐싱)."""
        exchange_name_lower = exchange_name.lower()

        if exchange_name_lower in self._exchanges:
            return self._exchanges[exchange_name_lower]

        try:
            config = self.settings.get_exchange_config(exchange_name_lower)

            if exchange_name_lower == "polymarket":
                exchange = dr_manhattan.Polymarket(config)
            elif exchange_name_lower == "opinion":
                exchange = dr_manhattan.Opinion(config)
            elif exchange_name_lower == "limitless":
                exchange = dr_manhattan.Limitless(config)
            else:
                # dr-manhattan의 create_exchange 사용
                exchange = dr_manhattan.create_exchange(exchange_name_lower, config)

            self._exchanges[exchange_name_lower] = exchange
            return exchange
        except Exception as e:
            print(f"거래소 초기화 실패 {exchange_name}: {e}")
            return None

    def list_available_exchanges(self) -> list[str]:
        """사용 가능한 거래소 목록 반환."""
        return dr_manhattan.list_exchanges()

    def get_all_exchanges(self) -> dict[str, Exchange]:
        """모든 거래소 인스턴스 반환."""
        available = self.list_available_exchanges()
        for name in available:
            self.get_exchange(name)
        return self._exchanges

