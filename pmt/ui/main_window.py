"""메인 윈도우."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QVBoxLayout, QWidget

from pmt.config.preset_loader import PresetLoader
from pmt.config.settings import Settings
from pmt.core import AccountManager, MarketManager
from pmt.storage.database import Database
from pmt.trading.exchange_adapter import ExchangeAdapter
from pmt.ui.widgets import AccountPanel, MarketBoard, MarketDetailPanel, PresetPanel


class MainWindow(QMainWindow):
    """PMT 메인 윈도우."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        super().__init__()
        self.settings = settings
        self._init_managers()
        self._init_ui()
        self._connect_signals()
        self._load_presets()
        self._load_initial_data()

    def _init_managers(self) -> None:
        """매니저 초기화."""
        # Database 초기화
        db_path = self.settings.data_dir / "pmt.db"
        self.database = Database(db_path)

        # ExchangeAdapter 초기화
        self.exchange_adapter = ExchangeAdapter(self.settings)

        # MarketManager 초기화
        self.market_manager = MarketManager(
            settings=self.settings,
            exchange_adapter=self.exchange_adapter,
            database=self.database,
        )

        # AccountManager 초기화
        self.account_manager = AccountManager(
            settings=self.settings,
            exchange_adapter=self.exchange_adapter,
        )

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

    def _connect_signals(self) -> None:
        """시그널 연결."""
        # Market Board 시그널
        self.market_board.market_selected.connect(self._on_market_selected)
        self.market_board.refresh_button.clicked.connect(self._on_refresh_markets)

        # MarketManager 시그널
        self.market_manager.markets_loaded.connect(self.market_board.set_markets)

        # Preset Panel 시그널
        self.preset_panel.preset_clicked.connect(self._on_preset_clicked)

        # AccountManager 시그널
        self.account_manager.balances_loaded.connect(self.account_panel.set_balances)
        self.account_manager.positions_loaded.connect(self.account_panel.set_positions)
        self.account_manager.orders_loaded.connect(self.account_panel.set_orders)

        # AccountPanel 시그널
        self.account_panel.refresh_requested.connect(self._on_refresh_account_data)
        self.account_panel.cancel_order_requested.connect(self._on_cancel_order)

    def _load_presets(self) -> None:
        """프리셋 로드."""
        loader = PresetLoader(self.settings.presets_dir)
        presets = loader.load_all()
        self.preset_panel.set_presets(presets)

    def _load_initial_data(self) -> None:
        """초기 데이터 로드."""
        # 마켓 데이터 로드
        self.market_manager.load_all_markets()

        # 계정 데이터 로드
        self.account_manager.load_all_balances()
        self.account_manager.load_all_positions()
        self.account_manager.load_all_orders()

    def _on_market_selected(self, exchange: str, market_id: str) -> None:
        """마켓 선택 시 호출."""
        # 백그라운드에서 마켓 상세 정보 가져오기
        market_data = self.market_manager.get_market(exchange, market_id)
        if market_data:
            self.market_detail.set_market(market_data)
        else:
            # 마켓을 찾을 수 없는 경우 기본 메시지 표시
            self.market_detail.clear()

    def _on_refresh_markets(self) -> None:
        """마켓 새로고침."""
        self.market_manager.load_all_markets(use_cache=False)

    def _on_refresh_account_data(self) -> None:
        """계정 데이터 새로고침."""
        # 모든 계정 데이터 새로고침
        self.account_manager.load_all_balances()
        self.account_manager.load_all_positions()
        self.account_manager.load_all_orders()

    def _on_cancel_order(self, exchange_name: str, order_id: str) -> None:
        """주문 취소."""
        success, error_msg = self.exchange_adapter.cancel_order(exchange_name, order_id)
        if success:
            # 주문 취소 성공 시 주문 목록 새로고침
            self.account_manager.load_all_orders()
        else:
            # 에러 메시지 표시 (필요시 QMessageBox 사용)
            print(f"주문 취소 실패: {error_msg}")

    def _on_preset_clicked(self, preset_name: str) -> None:
        """프리셋 클릭 시 호출."""
        # TODO: Risk Guard 검증 및 주문 실행
        print(f"프리셋 클릭: {preset_name}")

    def closeEvent(self, event) -> None:
        """윈도우 종료 시 리소스 정리."""
        self.market_manager.shutdown()
        self.account_manager.shutdown()
        event.accept()
