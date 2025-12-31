"""주문 실행자."""

from typing import Optional

from pmt.storage.database import Database
from pmt.storage.models import OrderLog
from pmt.trading.exchange_adapter import ExchangeAdapter


class OrderExecutor:
    """주문 실행 및 로깅."""

    def __init__(self, exchange_adapter: ExchangeAdapter, database: Database) -> None:
        """초기화."""
        self.exchange_adapter = exchange_adapter
        self.database = database

    def execute_order(
        self,
        exchange_name: str,
        market_id: str,
        outcome: str,
        side: str,
        price: float,
        size: float,
        preset_name: Optional[str] = None,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        주문 실행.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID
            outcome: Yes 또는 No
            side: BUY 또는 SELL
            price: 가격
            size: 수량
            preset_name: 프리셋 이름 (선택사항)

        Returns:
            (성공 여부, order_id 또는 None, 에러 메시지 또는 None)
        """
        # 주문 실행
        success, order_id, error_msg = self.exchange_adapter.create_order(
            exchange_name=exchange_name,
            market_id=market_id,
            outcome=outcome,
            side=side,
            price=price,
            size=size,
        )

        # 로깅
        self._log_order(
            exchange=exchange_name,
            market_id=market_id,
            outcome=outcome,
            side=side,
            price=price,
            size=size,
            order_id=order_id,
            success=success,
            error_message=error_msg,
            preset_name=preset_name,
        )

        return success, order_id, error_msg

    def _log_order(
        self,
        exchange: str,
        market_id: str,
        outcome: str,
        side: str,
        price: float,
        size: float,
        order_id: Optional[str],
        success: bool,
        error_message: Optional[str],
        preset_name: Optional[str],
    ) -> None:
        """주문 로그 저장."""
        try:
            session = self.database.get_session()
            try:
                log = OrderLog(
                    exchange=exchange,
                    market_id=market_id,
                    outcome=outcome,
                    side=side,
                    price=price,
                    size=size,
                    order_id=order_id,
                    status="success" if success else "failed",
                    error_message=error_message,
                    preset_name=preset_name,
                )
                session.add(log)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"주문 로그 저장 실패: {e}")
            finally:
                session.close()
        except Exception as e:
            print(f"주문 로그 저장 오류: {e}")

