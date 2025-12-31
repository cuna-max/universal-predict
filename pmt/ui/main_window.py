"""메인 윈도우."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QVBoxLayout, QWidget

from pmt.config.preset_loader import PresetLoader
from pmt.config.settings import Settings
from pmt.ui.widgets import AccountPanel, MarketBoard, MarketDetailPanel, PresetPanel


class MainWindow(QMainWindow):
    """PMT 메인 윈도우."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        super().__init__()
        self.settings = settings
        self._init_ui()
        self._load_presets()

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

        # 시그널 연결
        self.market_board.market_selected.connect(self._on_market_selected)
        self.preset_panel.preset_clicked.connect(self._on_preset_clicked)

        # 초기 데이터 로드 (더미 데이터로 화면 구성)
        self._load_dummy_data()

    def _load_presets(self) -> None:
        """프리셋 로드."""
        loader = PresetLoader(self.settings.presets_dir)
        presets = loader.load_all()
        self.preset_panel.set_presets(presets)

    def _on_market_selected(self, exchange: str, market_id: str) -> None:
        """마켓 선택 시 호출."""
        # TODO: 실제 마켓 데이터 가져와서 표시
        # 임시로 더미 데이터 사용
        market_data = {
            "question": f"선택된 마켓: {market_id}",
            "yes_price": 0.65,
            "no_price": 0.35,
            "close_time": None,
        }
        self.market_detail.set_market(market_data)

    def _on_preset_clicked(self, preset_name: str) -> None:
        """프리셋 클릭 시 호출."""
        # TODO: Risk Guard 검증 및 주문 실행
        print(f"프리셋 클릭: {preset_name}")

    def _load_dummy_data(self) -> None:
        """더미 데이터 로드 (화면 구성 확인용)."""
        # 더미 마켓 데이터
        dummy_markets = [
            {
                "exchange": "polymarket",
                "market_id": "fed-2026-rate",
                "question": "Will the Fed cut rates in 2026?",
                "yes_price": 0.64,
                "no_price": 0.36,
                "volume": 125000,
                "close_time": None,
                "status": "open",
            },
            {
                "exchange": "opinion",
                "market_id": "election-2024",
                "question": "Who will win the 2024 election?",
                "yes_price": 0.52,
                "no_price": 0.48,
                "volume": 89000,
                "close_time": None,
                "status": "open",
            },
            {
                "exchange": "limitless",
                "market_id": "btc-price-2025",
                "question": "Will BTC reach $100k in 2025?",
                "yes_price": 0.45,
                "no_price": 0.55,
                "volume": 156000,
                "close_time": None,
                "status": "open",
            },
        ]
        self.market_board.set_markets(dummy_markets)

        # 더미 잔고 데이터
        dummy_balances = [
            {"exchange": "polymarket", "balance": 1000.0},
            {"exchange": "opinion", "balance": 500.0},
            {"exchange": "limitless", "balance": 750.0},
        ]
        self.account_panel.set_balances(dummy_balances)

        # 더미 포지션 데이터
        dummy_positions = [
            {
                "exchange": "polymarket",
                "market_id": "fed-2026-rate",
                "outcome": "Yes",
                "size": 50,
                "avg_price": 0.62,
            }
        ]
        self.account_panel.set_positions(dummy_positions)

        # 더미 주문 데이터
        dummy_orders = [
            {
                "exchange": "polymarket",
                "market_id": "fed-2026-rate",
                "outcome": "No",
                "side": "BUY",
                "price": 0.35,
                "size": 30,
            }
        ]
        self.account_panel.set_orders(dummy_orders)

