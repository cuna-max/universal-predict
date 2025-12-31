"""통합 마켓 보드 위젯."""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MarketBoard(QWidget):
    """통합 마켓 보드 - 모든 거래소의 마켓을 테이블로 표시."""

    market_selected = Signal(str, str)  # exchange_name, market_id

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """초기화."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """UI 초기화."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 필터 영역
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(5)

        # 키워드 필터
        keyword_label = QLabel("키워드:")
        self.keyword_filter = QLineEdit()
        self.keyword_filter.setPlaceholderText("마켓 질문 검색...")
        filter_layout.addWidget(keyword_label)
        filter_layout.addWidget(self.keyword_filter)

        # 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setMinimumHeight(30)
        filter_layout.addWidget(self.refresh_button)

        layout.addLayout(filter_layout)

        # 마켓 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["거래소", "질문", "YES 가격", "NO 가격", "거래량", "마감 시간", "상태"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 테이블 클릭 시그널 연결
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

    def _on_selection_changed(self) -> None:
        """테이블 선택 변경 시 호출."""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            exchange_item = self.table.item(row, 0)
            market_id_item = self.table.item(row, 1)  # 질문 셀에 market_id를 data로 저장
            if exchange_item and market_id_item:
                exchange = exchange_item.text()
                market_id = market_id_item.data(Qt.ItemDataRole.UserRole)
                if market_id:
                    self.market_selected.emit(exchange, market_id)

    def set_markets(self, markets: list[dict]) -> None:
        """마켓 데이터 설정."""
        self.table.setRowCount(len(markets))

        for row, market in enumerate(markets):
            # 거래소
            exchange_item = QTableWidgetItem(market.get("exchange", ""))
            self.table.setItem(row, 0, exchange_item)

            # 질문 (market_id를 UserRole에 저장)
            question_item = QTableWidgetItem(market.get("question", ""))
            question_item.setData(Qt.ItemDataRole.UserRole, market.get("market_id", ""))
            self.table.setItem(row, 1, question_item)

            # YES 가격
            yes_price = market.get("yes_price", 0.0)
            yes_item = QTableWidgetItem(f"{yes_price:.3f}" if yes_price else "N/A")
            yes_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, yes_item)

            # NO 가격
            no_price = market.get("no_price", 0.0)
            no_item = QTableWidgetItem(f"{no_price:.3f}" if no_price else "N/A")
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, no_item)

            # 거래량
            volume = market.get("volume", 0.0)
            volume_item = QTableWidgetItem(f"{volume:,.0f}" if volume else "0")
            volume_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, volume_item)

            # 마감 시간
            close_time = market.get("close_time")
            if close_time:
                if isinstance(close_time, datetime):
                    close_str = close_time.strftime("%Y-%m-%d %H:%M")
                else:
                    close_str = str(close_time)
            else:
                close_str = "N/A"
            close_item = QTableWidgetItem(close_str)
            self.table.setItem(row, 5, close_item)

            # 상태
            status = market.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 6, status_item)

        self.table.resizeColumnsToContents()

    def get_selected_market(self) -> Optional[tuple[str, str]]:
        """선택된 마켓 반환 (exchange, market_id)."""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            exchange_item = self.table.item(row, 0)
            market_id_item = self.table.item(row, 1)
            if exchange_item and market_id_item:
                exchange = exchange_item.text()
                market_id = market_id_item.data(Qt.ItemDataRole.UserRole)
                return (exchange, market_id) if market_id else None
        return None

