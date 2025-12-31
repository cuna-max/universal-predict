"""메인 윈도우."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget

from pmt.config.settings import Settings
from pmt.core.market_manager import MarketManager
from pmt.core.preset_manager import PresetManager
from pmt.core.risk_guard import RiskGuard
from pmt.storage.database import Database
from pmt.trading.exchange_adapter import ExchangeAdapter
from pmt.trading.order_executor import OrderExecutor
from pmt.ui.widgets import AccountPanel, ConfirmDialog, MarketBoard, MarketDetailPanel, PresetPanel


class MainWindow(QMainWindow):
    """PMT 메인 윈도우."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        super().__init__()
        self.settings = settings

        # 핵심 컴포넌트 초기화
        self.database = Database(settings.data_dir / "pmt.db")
        self.exchange_adapter = ExchangeAdapter(settings)
        self.market_manager = MarketManager(settings, self.exchange_adapter, self.database)
        self.preset_manager = PresetManager(settings)
        self.risk_guard = RiskGuard(settings, self.exchange_adapter)
        self.order_executor = OrderExecutor(self.exchange_adapter, self.database)

        # 자동 새로고침 타이머
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_markets)
        self.refresh_timer.setInterval(settings.cache_refresh_interval * 1000)

        self._init_ui()
        self._connect_signals()
        self._load_initial_data()

    def _init_ui(self) -> None:
        """UI 초기화."""
        self.setWindowTitle("Prediction Market Terminal")
        self.setMinimumSize(1400, 900)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃 (좌우 분할)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Splitter로 좌우 분할
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Horizontal)

        # 좌측: Market Board
        self.market_board = MarketBoard()
        splitter.addWidget(self.market_board)

        # 우측: 상세 정보, 프리셋, 계정 패널
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        # Market Detail Panel
        self.market_detail = MarketDetailPanel()
        self.market_detail.setMinimumHeight(200)
        right_layout.addWidget(self.market_detail)

        # Preset Panel
        self.preset_panel = PresetPanel()
        self.preset_panel.setMinimumHeight(250)
        right_layout.addWidget(self.preset_panel)

        # Account Panel
        self.account_panel = AccountPanel()
        self.account_panel.setMinimumHeight(300)
        right_layout.addWidget(self.account_panel)

        splitter.addWidget(right_panel)

        # Splitter 비율 설정 (좌측 60%, 우측 40%)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # 새로고침 버튼 연결
        self.market_board.refresh_button.clicked.connect(self._refresh_markets)

    def _connect_signals(self) -> None:
        """시그널 연결."""
        # 마켓 선택
        self.market_board.market_selected.connect(self._on_market_selected)

        # 프리셋 클릭
        self.preset_panel.preset_clicked.connect(self._on_preset_clicked)

        # 마켓 매니저 시그널
        self.market_manager.markets_loaded.connect(self._on_markets_loaded)
        self.market_manager.loading_started.connect(self._on_loading_started)
        self.market_manager.loading_finished.connect(self._on_loading_finished)

        # 계정 패널 시그널
        self.account_panel.refresh_requested.connect(self._refresh_account_info)
        self.account_panel.cancel_order_requested.connect(self._on_cancel_order_requested)

    def _load_initial_data(self) -> None:
        """초기 데이터 로드."""
        # 프리셋 로드
        presets = self.preset_manager.get_all_presets()
        self.preset_panel.set_presets(presets)

        # 마켓 데이터 로드
        self._refresh_markets()

        # 계정 정보 로드
        self._refresh_account_info()

        # 자동 새로고침 시작
        self.refresh_timer.start()

    def _refresh_markets(self) -> None:
        """마켓 데이터 새로고침."""
        self.market_manager.load_all_markets(use_cache=True)

    def _on_loading_started(self) -> None:
        """로딩 시작."""
        self.market_board.refresh_button.setEnabled(False)
        self.market_board.refresh_button.setText("로딩 중...")

    def _on_loading_finished(self) -> None:
        """로딩 완료."""
        self.market_board.refresh_button.setEnabled(True)
        self.market_board.refresh_button.setText("새로고침")

    def _on_markets_loaded(self, markets: list[dict]) -> None:
        """마켓 데이터 로드 완료."""
        self.market_board.set_markets(markets)

    def _on_market_selected(self, exchange: str, market_id: str) -> None:
        """마켓 선택 시 호출."""
        # 실제 마켓 데이터 조회
        market_data = self.market_manager.get_market(exchange, market_id)
        if market_data:
            self.market_detail.set_market(market_data)

            # 포지션 정보 조회
            positions = self.exchange_adapter.fetch_positions(exchange)
            market_positions = [p for p in positions if p.get("market_id") == market_id]
            if market_positions:
                # 포지션 요약 생성
                yes_pos = sum(p.get("size", 0) for p in market_positions if p.get("outcome") == "Yes")
                no_pos = sum(p.get("size", 0) for p in market_positions if p.get("outcome") == "No")
                market_data["position"] = {"yes": yes_pos, "no": no_pos}
                self.market_detail.set_market(market_data)
        else:
            # 마켓 데이터를 찾을 수 없는 경우
            self.market_detail.clear()

    def _on_preset_clicked(self, preset_name: str) -> None:
        """프리셋 클릭 시 호출."""
        preset = self.preset_manager.get_preset(preset_name)
        if not preset:
            QMessageBox.warning(self, "오류", f"프리셋을 찾을 수 없습니다: {preset_name}")
            return

        # Risk Guard 검증
        exchange = preset.get("exchange", "")
        market_id = preset.get("market_id", "")
        outcome = preset.get("outcome", "")
        side = preset.get("side", "")
        price = preset.get("price", 0.0)
        size = preset.get("size", 0.0)

        # 현재 마켓 가격 조회 (가격 검증용)
        current_price = None
        market_data = self.market_manager.get_market(exchange, market_id)
        if market_data:
            if outcome.upper() == "YES":
                current_price = market_data.get("yes_price")
            else:
                current_price = market_data.get("no_price")

        # Risk Guard 검증
        is_valid, error_msg = self.risk_guard.validate_order(
            exchange_name=exchange,
            price=price,
            size=size,
            market_id=market_id,
            allowed_market_ids=[market_id],  # Preset에 정의된 마켓만 허용
            current_market_price=current_price,
        )

        if not is_valid:
            QMessageBox.warning(self, "주문 검증 실패", error_msg or "알 수 없는 오류")
            return

        # Dry Run 모드 체크 (Risk Guard에서 제거했으므로 여기서 체크)
        if self.settings.dry_run_mode:
            QMessageBox.information(
                self,
                "Dry Run 모드",
                "Dry Run 모드가 활성화되어 있습니다. 실제 주문이 실행되지 않습니다.",
            )
            # Dry Run 모드에서도 로깅은 수행 (OrderExecutor에서 처리)

        # 확인 다이얼로그 표시
        if not ConfirmDialog.show_confirmation(preset, self.settings.dry_run_mode, self):
            return

        # 주문 실행
        success, order_id, error_msg = self.order_executor.execute_order(
            exchange_name=exchange,
            market_id=market_id,
            outcome=outcome,
            side=side,
            price=price,
            size=size,
            preset_name=preset_name,
        )

        # 결과 표시
        if success:
            if self.settings.dry_run_mode:
                QMessageBox.information(self, "주문 완료 (Dry Run)", f"Dry Run 모드: 주문이 시뮬레이션되었습니다.\n주문 ID: {order_id or 'N/A'}")
            else:
                QMessageBox.information(self, "주문 완료", f"주문이 성공적으로 실행되었습니다.\n주문 ID: {order_id or 'N/A'}")
            # 계정 정보 새로고침
            self._refresh_account_info()
        else:
            QMessageBox.critical(self, "주문 실패", f"주문 실행에 실패했습니다.\n{error_msg or '알 수 없는 오류'}")

    def _refresh_account_info(self) -> None:
        """계정 정보 새로고침."""
        # 잔고 조회
        balances = []
        for exchange_name in self.exchange_adapter.list_available_exchanges():
            balance = self.exchange_adapter.fetch_balance(exchange_name)
            if balance is not None:
                balances.append({"exchange": exchange_name, "balance": balance})
        self.account_panel.set_balances(balances)

        # 포지션 조회
        all_positions = []
        for exchange_name in self.exchange_adapter.list_available_exchanges():
            positions = self.exchange_adapter.fetch_positions(exchange_name)
            all_positions.extend(positions)
        self.account_panel.set_positions(all_positions)

        # 활성 주문 조회
        all_orders = []
        for exchange_name in self.exchange_adapter.list_available_exchanges():
            orders = self.exchange_adapter.fetch_orders(exchange_name)
            all_orders.extend(orders)
        self.account_panel.set_orders(all_orders)

    def _on_cancel_order_requested(self, exchange_name: str, order_id: str) -> None:
        """주문 취소 요청 처리."""
        success, error_msg = self.exchange_adapter.cancel_order(exchange_name, order_id)
        if success:
            QMessageBox.information(self, "주문 취소 완료", f"주문이 성공적으로 취소되었습니다.\n주문 ID: {order_id}")
            # 주문 목록 새로고침
            self._refresh_account_info()
        else:
            QMessageBox.critical(self, "주문 취소 실패", f"주문 취소에 실패했습니다.\n{error_msg or '알 수 없는 오류'}")

    def closeEvent(self, event) -> None:
        """윈도우 종료 시 리소스 정리."""
        self.refresh_timer.stop()
        self.market_manager.shutdown()
        event.accept()

