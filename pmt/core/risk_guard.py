"""리스크 가드 시스템."""

from typing import Optional

from pmt.config.settings import Settings


class RiskGuard:
    """주문 실행 전 리스크 검증."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        self.settings = settings

    def validate_order(
        self,
        price: float,
        size: float,
        market_id: str,
        allowed_market_ids: Optional[list[str]] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        주문 유효성 검증.

        Returns:
            (is_valid, error_message)
        """
        # Dry Run 모드 체크
        if self.settings.dry_run_mode:
            return False, "Dry Run 모드: 실제 주문이 차단되었습니다"

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

        return True, None

