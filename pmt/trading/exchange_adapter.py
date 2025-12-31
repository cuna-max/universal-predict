"""dr-manhattan 거래소 어댑터."""

from datetime import datetime
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

    def fetch_markets(self, exchange_name: str) -> list[dict[str, Any]]:
        """
        거래소의 마켓 목록 조회.

        Returns:
            정규화된 마켓 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return []

        try:
            markets = exchange.fetch_markets()
            normalized_markets = []
            for market in markets:
                normalized = self._normalize_market_data(exchange_name, market)
                if normalized:
                    normalized_markets.append(normalized)
            return normalized_markets
        except Exception as e:
            print(f"마켓 조회 실패 {exchange_name}: {e}")
            return []

    def fetch_balance(self, exchange_name: str) -> Optional[float]:
        """
        거래소 잔고 조회.

        Returns:
            잔고 금액 (실패 시 None)
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return None

        try:
            balance = exchange.fetch_balance()
            if isinstance(balance, (int, float)):
                return float(balance)
            # balance가 dict인 경우 처리
            if isinstance(balance, dict):
                # 일반적인 키 이름들 시도
                for key in ["balance", "available", "total", "usd"]:
                    if key in balance:
                        return float(balance[key])
            return None
        except Exception as e:
            print(f"잔고 조회 실패 {exchange_name}: {e}")
            return None

    def fetch_positions(self, exchange_name: str) -> list[dict[str, Any]]:
        """
        거래소 포지션 조회.

        Returns:
            정규화된 포지션 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return []

        try:
            positions = exchange.fetch_positions()
            normalized_positions = []
            for pos in positions:
                normalized = self._normalize_position_data(exchange_name, pos)
                if normalized:
                    normalized_positions.append(normalized)
            return normalized_positions
        except Exception as e:
            print(f"포지션 조회 실패 {exchange_name}: {e}")
            return []

    def fetch_orders(self, exchange_name: str, market_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        거래소 활성 주문 조회.

        Args:
            exchange_name: 거래소 이름
            market_id: 특정 마켓 필터링 (선택사항)

        Returns:
            정규화된 주문 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return []

        try:
            orders = exchange.fetch_orders(market_id=market_id) if market_id else exchange.fetch_orders()
            normalized_orders = []
            for order in orders:
                normalized = self._normalize_order_data(exchange_name, order)
                if normalized:
                    normalized_orders.append(normalized)
            return normalized_orders
        except Exception as e:
            print(f"주문 조회 실패 {exchange_name}: {e}")
            return []

    def create_order(
        self,
        exchange_name: str,
        market_id: str,
        outcome: str,
        side: str,
        price: float,
        size: float,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        주문 생성.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID
            outcome: Yes 또는 No
            side: BUY 또는 SELL
            price: 가격
            size: 수량

        Returns:
            (성공 여부, order_id 또는 None, 에러 메시지 또는 None)
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return False, None, f"거래소를 찾을 수 없습니다: {exchange_name}"

        try:
            result = exchange.create_order(
                market_id=market_id,
                outcome=outcome,
                side=side,
                price=price,
                size=size,
            )
            # result가 dict인 경우 order_id 추출
            if isinstance(result, dict):
                order_id = result.get("order_id") or result.get("id") or result.get("orderId")
                return True, order_id, None
            # result가 문자열인 경우 (order_id)
            if isinstance(result, str):
                return True, result, None
            return True, None, None
        except Exception as e:
            error_msg = str(e)
            print(f"주문 생성 실패 {exchange_name}: {error_msg}")
            return False, None, error_msg

    def cancel_order(self, exchange_name: str, order_id: str) -> tuple[bool, Optional[str]]:
        """
        주문 취소.

        Args:
            exchange_name: 거래소 이름
            order_id: 주문 ID

        Returns:
            (성공 여부, 에러 메시지 또는 None)
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return False, f"거래소를 찾을 수 없습니다: {exchange_name}"

        try:
            exchange.cancel_order(order_id)
            return True, None
        except Exception as e:
            error_msg = str(e)
            print(f"주문 취소 실패 {exchange_name}: {error_msg}")
            return False, error_msg

    def fetch_market(self, exchange_name: str, market_id: str) -> Optional[dict[str, Any]]:
        """
        특정 마켓 상세 정보 조회.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID

        Returns:
            정규화된 마켓 데이터 또는 None
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return None

        try:
            market = exchange.fetch_market(market_id)
            if market:
                return self._normalize_market_data(exchange_name, market)
            return None
        except Exception as e:
            print(f"마켓 조회 실패 {exchange_name}/{market_id}: {e}")
            return None

    def _normalize_market_data(self, exchange_name: str, market: Any) -> Optional[dict[str, Any]]:
        """마켓 데이터 정규화."""
        try:
            # dr-manhattan의 표준 형식 가정
            normalized = {
                "exchange": exchange_name.lower(),
                "market_id": str(market.get("market_id") or market.get("id") or ""),
                "question": str(market.get("question") or market.get("title") or ""),
                "yes_price": self._safe_float(market.get("yes_price") or market.get("yesPrice")),
                "no_price": self._safe_float(market.get("no_price") or market.get("noPrice")),
                "volume": self._safe_float(market.get("volume") or market.get("volume24h") or 0),
                "close_time": self._parse_datetime(market.get("close_time") or market.get("closeTime")),
                "status": str(market.get("status") or "open").lower(),
            }
            # 필수 필드 검증
            if not normalized["market_id"] or not normalized["question"]:
                return None
            return normalized
        except Exception as e:
            print(f"마켓 데이터 정규화 실패: {e}")
            return None

    def _normalize_position_data(self, exchange_name: str, position: Any) -> Optional[dict[str, Any]]:
        """포지션 데이터 정규화."""
        try:
            normalized = {
                "exchange": exchange_name.lower(),
                "market_id": str(position.get("market_id") or position.get("id") or ""),
                "outcome": str(position.get("outcome") or "Yes"),
                "size": self._safe_float(position.get("size") or position.get("quantity") or 0),
                "avg_price": self._safe_float(position.get("avg_price") or position.get("averagePrice") or 0),
            }
            if not normalized["market_id"]:
                return None
            return normalized
        except Exception as e:
            print(f"포지션 데이터 정규화 실패: {e}")
            return None

    def _normalize_order_data(self, exchange_name: str, order: Any) -> Optional[dict[str, Any]]:
        """주문 데이터 정규화."""
        try:
            normalized = {
                "exchange": exchange_name.lower(),
                "order_id": str(order.get("order_id") or order.get("id") or order.get("orderId") or ""),
                "market_id": str(order.get("market_id") or order.get("marketId") or ""),
                "outcome": str(order.get("outcome") or "Yes"),
                "side": str(order.get("side") or "BUY").upper(),
                "price": self._safe_float(order.get("price") or 0),
                "size": self._safe_float(order.get("size") or order.get("quantity") or 0),
            }
            if not normalized["order_id"] or not normalized["market_id"]:
                return None
            return normalized
        except Exception as e:
            print(f"주문 데이터 정규화 실패: {e}")
            return None

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """안전한 float 변환."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_datetime(value: Any) -> Optional[datetime]:
        """datetime 파싱."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            # ISO format 시도
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None

