"""계정 및 포지션 패널."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class AccountPanel(QWidget):
    """계정 정보, 포지션, 활성 주문을 표시하는 패널."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """초기화."""
        super().__init__(parent)
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

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(
            ["거래소", "마켓", "Outcome", "Side", "가격", "수량"]
        )
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        orders_layout.addWidget(self.orders_table)

        cancel_order_btn = QPushButton("선택 주문 취소")
        cancel_order_btn.clicked.connect(self._cancel_selected_order)
        orders_layout.addWidget(cancel_order_btn)

        refresh_orders_btn = QPushButton("주문 새로고침")
        refresh_orders_btn.clicked.connect(self._refresh_orders)
        orders_layout.addWidget(refresh_orders_btn)

        self.tabs.addTab(self.orders_tab, "활성 주문")

    def _refresh_balance(self) -> None:
        """잔고 새로고침 (나중에 실제 로직 연결)."""
        pass

    def _refresh_positions(self) -> None:
        """포지션 새로고침 (나중에 실제 로직 연결)."""
        pass

    def _refresh_orders(self) -> None:
        """주문 새로고침 (나중에 실제 로직 연결)."""
        pass

    def _cancel_selected_order(self) -> None:
        """선택된 주문 취소 (나중에 실제 로직 연결)."""
        pass

    def set_balances(self, balances: list[dict]) -> None:
        """잔고 데이터 설정."""
        self.balance_table.setRowCount(len(balances))
        for row, balance in enumerate(balances):
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
        self.position_table.setRowCount(len(positions))
        for row, position in enumerate(positions):
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
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
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
        self.orders_table.resizeColumnsToContents()

