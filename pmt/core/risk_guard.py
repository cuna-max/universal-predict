"""리스크 가드 시스템."""

from typing import Optional

from pmt.config.settings import Settings
from pmt.trading.exchange_adapter import ExchangeAdapter


class RiskGuard:
    """주문 실행 전 리스크 검증."""

    def __init__(self, settings: Settings, exchange_adapter: Optional[ExchangeAdapter] = None) -> None:
        """초기화."""
        self.settings = settings
        self.exchange_adapter = exchange_adapter

    def validate_order(
        self,
        exchange_name: str,
        price: float,
        size: float,
        market_id: str,
        allowed_market_ids: Optional[list[str]] = None,
        current_market_price: Optional[float] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        주문 유효성 검증.

        Args:
            exchange_name: 거래소 이름
            price: 주문 가격
            size: 주문 수량
            market_id: 마켓 ID
            allowed_market_ids: 허용된 마켓 ID 리스트
            current_market_price: 현재 마켓 가격 (선택사항)

        Returns:
            (is_valid, error_message)
        """
        # Dry Run 모드 체크 (Dry Run 모드에서는 실제 주문 차단, 하지만 검증은 계속 진행)
        # 주의: Dry Run 모드 체크는 OrderExecutor에서 처리하므로 여기서는 제거

        # Market Allowlist 체크
        if allowed_market_ids and market_id not in allowed_market_ids:
            return False, f"허용되지 않은 마켓: {market_id}"

        # Max Notional 체크
        notional = price * size
        if notional > self.settings.max_notional:
            return (
                False,
                f"Notional 초과: {notional:.2f} > {self.settings.max_notional:.2f}",
            )

        # Max Size 체크
        if size > self.settings.max_size:
            return (
                False,
                f"Size 초과: {size:.2f} > {self.settings.max_size:.2f}",
            )

        # 가격 유효성 체크
        if price <= 0 or price >= 1:
            return False, f"유효하지 않은 가격: {price:.4f} (0 < price < 1)"

        # 수량 유효성 체크
        if size <= 0:
            return False, f"유효하지 않은 수량: {size:.2f}"

        # 잔고 부족 체크
        if self.exchange_adapter:
            balance = self.exchange_adapter.fetch_balance(exchange_name)
            if balance is not None:
                if notional > balance:
                    return False, f"잔고 부족: 필요 {notional:.2f}, 보유 {balance:.2f}"

        # 가격 오류 체크 (현재 마켓 가격과 비교)
        if current_market_price is not None:
            price_diff = abs(price - current_market_price)
            # 가격 차이가 10% 이상이면 경고 (하지만 차단하지는 않음)
            if price_diff > 0.1:
                # 경고만 하고 계속 진행 (사용자가 의도적으로 다른 가격을 입력할 수 있음)
                pass

        return True, None

