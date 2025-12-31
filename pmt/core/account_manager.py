"""계정 데이터 관리자."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from PySide6.QtCore import QObject, Signal

from pmt.config.settings import Settings
from pmt.trading.exchange_adapter import ExchangeAdapter


class AccountManager(QObject):
    """계정 데이터 로딩 관리 (잔고, 포지션, 주문)."""

    balances_loaded = Signal(list)  # 정규화된 잔고 데이터 리스트
    positions_loaded = Signal(list)  # 정규화된 포지션 데이터 리스트
    orders_loaded = Signal(list)  # 정규화된 주문 데이터 리스트
    loading_started = Signal()
    loading_finished = Signal()

    def __init__(self, settings: Settings, exchange_adapter: ExchangeAdapter) -> None:
        """초기화."""
        super().__init__()
        self.settings = settings
        self.exchange_adapter = exchange_adapter
        self.executor = ThreadPoolExecutor(max_workers=5)

    def load_all_balances(self) -> None:
        """모든 거래소의 잔고 데이터 병렬 로딩."""
        self.loading_started.emit()

        def _load():
            all_balances = []
            available_exchanges = self.exchange_adapter.list_available_exchanges()
            
            if not available_exchanges:
                self.balances_loaded.emit([])
                self.loading_finished.emit()
                return

            futures = {}

            for exchange_name in available_exchanges:
                future = self.executor.submit(self.exchange_adapter.fetch_balance, exchange_name)
                futures[future] = exchange_name

            for future in as_completed(futures):
                exchange_name = futures[future]
                try:
                    balance = future.result()
                    if balance is not None:
                        all_balances.append({"exchange": exchange_name, "balance": balance})
                except Exception as e:
                    print(f"[ERROR] 잔고 로딩 실패 {exchange_name}: {e}")

            self.balances_loaded.emit(all_balances)
            self.loading_finished.emit()

        # 백그라운드 스레드에서 실행
        self.executor.submit(_load)

    def load_all_positions(self) -> None:
        """모든 거래소의 포지션 데이터 병렬 로딩."""
        self.loading_started.emit()

        def _load():
            all_positions = []
            available_exchanges = self.exchange_adapter.list_available_exchanges()
            futures = {}

            for exchange_name in available_exchanges:
                future = self.executor.submit(self.exchange_adapter.fetch_positions, exchange_name)
                futures[future] = exchange_name

            for future in as_completed(futures):
                exchange_name = futures[future]
                try:
                    positions = future.result()
                    all_positions.extend(positions)
                except Exception as e:
                    print(f"포지션 로딩 실패 {exchange_name}: {e}")

            self.positions_loaded.emit(all_positions)
            self.loading_finished.emit()

        # 백그라운드 스레드에서 실행
        self.executor.submit(_load)

    def load_all_orders(self) -> None:
        """모든 거래소의 주문 데이터 병렬 로딩."""
        self.loading_started.emit()

        def _load():
            all_orders = []
            available_exchanges = self.exchange_adapter.list_available_exchanges()
            futures = {}

            for exchange_name in available_exchanges:
                future = self.executor.submit(self.exchange_adapter.fetch_orders, exchange_name)
                futures[future] = exchange_name

            for future in as_completed(futures):
                exchange_name = futures[future]
                try:
                    orders = future.result()
                    all_orders.extend(orders)
                except Exception as e:
                    print(f"주문 로딩 실패 {exchange_name}: {e}")

            self.orders_loaded.emit(all_orders)
            self.loading_finished.emit()

        # 백그라운드 스레드에서 실행
        self.executor.submit(_load)

    def shutdown(self) -> None:
        """리소스 정리."""
        self.executor.shutdown(wait=True)

