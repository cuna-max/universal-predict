"""계정 및 포지션 패널."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class AccountPanel(QWidget):
    """계정 정보, 포지션, 활성 주문을 표시하는 패널."""

    refresh_requested = Signal()  # 전체 새로고침 요청
    cancel_order_requested = Signal(str, str)  # exchange_name, order_id

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """초기화."""
        super().__init__(parent)
        self._all_balances: list[dict] = []
        self._all_positions: list[dict] = []
        self._all_orders: list[dict] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """UI 초기화."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 제목
        title_label = QLabel("계정 & 포지션")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 탭 위젯
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 잔고 탭
        self.balance_tab = QWidget()
        balance_layout = QVBoxLayout(self.balance_tab)
        balance_layout.setContentsMargins(5, 5, 5, 5)

        # 거래소 필터
        balance_filter_layout = QHBoxLayout()
        balance_filter_label = QLabel("거래소:")
        balance_filter_label.setMinimumWidth(60)
        self.balance_exchange_filter = QComboBox()
        self.balance_exchange_filter.addItem("전체", None)
        self.balance_exchange_filter.addItem("Polymarket", "polymarket")
        self.balance_exchange_filter.addItem("Opinion", "opinion")
        self.balance_exchange_filter.addItem("Limitless", "limitless")
        self.balance_exchange_filter.currentIndexChanged.connect(self._apply_balance_filter)
        balance_filter_layout.addWidget(balance_filter_label)
        balance_filter_layout.addWidget(self.balance_exchange_filter)
        balance_filter_layout.addStretch()
        balance_layout.addLayout(balance_filter_layout)

        self.balance_table = QTableWidget()
        self.balance_table.setColumnCount(2)
        self.balance_table.setHorizontalHeaderLabels(["거래소", "잔고"])
        self.balance_table.horizontalHeader().setStretchLastSection(True)
        self.balance_table.setAlternatingRowColors(True)
        self.balance_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        balance_layout.addWidget(self.balance_table)

        refresh_balance_btn = QPushButton("잔고 새로고침")
        refresh_balance_btn.clicked.connect(self._refresh_balance)
        balance_layout.addWidget(refresh_balance_btn)

        self.tabs.addTab(self.balance_tab, "잔고")

        # 포지션 탭
        self.position_tab = QWidget()
        position_layout = QVBoxLayout(self.position_tab)
        position_layout.setContentsMargins(5, 5, 5, 5)

        # 거래소 필터
        position_filter_layout = QHBoxLayout()
        position_filter_label = QLabel("거래소:")
        position_filter_label.setMinimumWidth(60)
        self.position_exchange_filter = QComboBox()
        self.position_exchange_filter.addItem("전체", None)
        self.position_exchange_filter.addItem("Polymarket", "polymarket")
        self.position_exchange_filter.addItem("Opinion", "opinion")
        self.position_exchange_filter.addItem("Limitless", "limitless")
        self.position_exchange_filter.currentIndexChanged.connect(self._apply_position_filter)
        position_filter_layout.addWidget(position_filter_label)
        position_filter_layout.addWidget(self.position_exchange_filter)
        position_filter_layout.addStretch()
        position_layout.addLayout(position_filter_layout)

        self.position_table = QTableWidget()
        self.position_table.setColumnCount(5)
        self.position_table.setHorizontalHeaderLabels(
            ["거래소", "마켓", "Outcome", "수량", "평균가"]
        )
        self.position_table.horizontalHeader().setStretchLastSection(True)
        self.position_table.setAlternatingRowColors(True)
        self.position_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        position_layout.addWidget(self.position_table)

        refresh_position_btn = QPushButton("포지션 새로고침")
        refresh_position_btn.clicked.connect(self._refresh_positions)
        position_layout.addWidget(refresh_position_btn)

        self.tabs.addTab(self.position_tab, "포지션")

        # 활성 주문 탭
        self.orders_tab = QWidget()
        orders_layout = QVBoxLayout(self.orders_tab)
        orders_layout.setContentsMargins(5, 5, 5, 5)

        # 거래소 필터
        orders_filter_layout = QHBoxLayout()
        orders_filter_label = QLabel("거래소:")
        orders_filter_label.setMinimumWidth(60)
        self.orders_exchange_filter = QComboBox()
        self.orders_exchange_filter.addItem("전체", None)
        self.orders_exchange_filter.addItem("Polymarket", "polymarket")
        self.orders_exchange_filter.addItem("Opinion", "opinion")
        self.orders_exchange_filter.addItem("Limitless", "limitless")
        self.orders_exchange_filter.currentIndexChanged.connect(self._apply_orders_filter)
        orders_filter_layout.addWidget(orders_filter_label)
        orders_filter_layout.addWidget(self.orders_exchange_filter)
        orders_filter_layout.addStretch()
        orders_layout.addLayout(orders_filter_layout)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(
            ["거래소", "마켓", "Outcome", "Side", "가격", "수량", "주문 ID"]
        )
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        orders_layout.addWidget(self.orders_table)

        cancel_order_btn = QPushButton("선택 주문 취소")
        cancel_order_btn.clicked.connect(self._cancel_selected_order)
        orders_layout.addWidget(cancel_order_btn)

        refresh_orders_btn = QPushButton("주문 새로고침")
        refresh_orders_btn.clicked.connect(self._refresh_orders)
        orders_layout.addWidget(refresh_orders_btn)

        self.tabs.addTab(self.orders_tab, "활성 주문")

    def _refresh_balance(self) -> None:
        """잔고 새로고침 요청."""
        self.refresh_requested.emit()

    def _refresh_positions(self) -> None:
        """포지션 새로고침 요청."""
        self.refresh_requested.emit()

    def _refresh_orders(self) -> None:
        """주문 새로고침 요청."""
        self.refresh_requested.emit()

    def _cancel_selected_order(self) -> None:
        """선택된 주문 취소 요청."""
        selected_rows = self.orders_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "오류", "취소할 주문을 선택하세요.")
            return

        row = selected_rows[0].row()
        exchange_item = self.orders_table.item(row, 0)
        order_id_item = self.orders_table.item(row, 6)  # 주문 ID 컬럼

        if not exchange_item or not order_id_item:
            QMessageBox.warning(self, "오류", "주문 정보를 찾을 수 없습니다.")
            return

        exchange = exchange_item.text()
        order_id = order_id_item.text()

        if not order_id:
            QMessageBox.warning(self, "오류", "주문 ID가 없습니다.")
            return

        # 확인 다이얼로그
        reply = QMessageBox.question(
            self,
            "주문 취소 확인",
            f"주문을 취소하시겠습니까?\n거래소: {exchange}\n주문 ID: {order_id}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cancel_order_requested.emit(exchange, order_id)

    def set_balances(self, balances: list[dict]) -> None:
        """잔고 데이터 설정."""
        self._all_balances = balances
        self._apply_balance_filter()

    def _apply_balance_filter(self) -> None:
        """잔고 필터 적용."""
        selected_exchange = self.balance_exchange_filter.currentData()
        
        filtered_balances = []
        for balance in self._all_balances:
            if selected_exchange is not None:
                if balance.get("exchange", "").lower() != selected_exchange.lower():
                    continue
            filtered_balances.append(balance)

        self.balance_table.setRowCount(len(filtered_balances))
        for row, balance in enumerate(filtered_balances):
            exchange_item = QTableWidgetItem(balance.get("exchange", ""))
            self.balance_table.setItem(row, 0, exchange_item)

            balance_value = balance.get("balance", 0.0)
            balance_item = QTableWidgetItem(f"{balance_value:,.2f}")
            balance_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.balance_table.setItem(row, 1, balance_item)
        self.balance_table.resizeColumnsToContents()

    def set_positions(self, positions: list[dict]) -> None:
        """포지션 데이터 설정."""
        self._all_positions = positions
        self._apply_position_filter()

    def _apply_position_filter(self) -> None:
        """포지션 필터 적용."""
        selected_exchange = self.position_exchange_filter.currentData()
        
        filtered_positions = []
        for position in self._all_positions:
            if selected_exchange is not None:
                if position.get("exchange", "").lower() != selected_exchange.lower():
                    continue
            filtered_positions.append(position)

        self.position_table.setRowCount(len(filtered_positions))
        for row, position in enumerate(filtered_positions):
            self.position_table.setItem(row, 0, QTableWidgetItem(position.get("exchange", "")))
            self.position_table.setItem(row, 1, QTableWidgetItem(position.get("market_id", "")))
            self.position_table.setItem(row, 2, QTableWidgetItem(position.get("outcome", "")))
            size_item = QTableWidgetItem(str(position.get("size", 0)))
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.position_table.setItem(row, 3, size_item)
            avg_price_item = QTableWidgetItem(f"{position.get('avg_price', 0.0):.3f}")
            avg_price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.position_table.setItem(row, 4, avg_price_item)
        self.position_table.resizeColumnsToContents()

    def set_orders(self, orders: list[dict]) -> None:
        """활성 주문 데이터 설정."""
        self._all_orders = orders
        self._apply_orders_filter()

    def _apply_orders_filter(self) -> None:
        """주문 필터 적용."""
        selected_exchange = self.orders_exchange_filter.currentData()
        
        filtered_orders = []
        for order in self._all_orders:
            if selected_exchange is not None:
                if order.get("exchange", "").lower() != selected_exchange.lower():
                    continue
            filtered_orders.append(order)

        self.orders_table.setRowCount(len(filtered_orders))
        for row, order in enumerate(filtered_orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(order.get("exchange", "")))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.get("market_id", "")))
            self.orders_table.setItem(row, 2, QTableWidgetItem(order.get("outcome", "")))
            self.orders_table.setItem(row, 3, QTableWidgetItem(order.get("side", "")))
            price_item = QTableWidgetItem(f"{order.get('price', 0.0):.3f}")
            price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.orders_table.setItem(row, 4, price_item)
            size_item = QTableWidgetItem(str(order.get("size", 0)))
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.orders_table.setItem(row, 5, size_item)
            # 주문 ID 추가
            order_id_item = QTableWidgetItem(order.get("order_id", ""))
            self.orders_table.setItem(row, 6, order_id_item)
        self.orders_table.resizeColumnsToContents()

