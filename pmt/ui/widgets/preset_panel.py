"""프리셋 주문 패널."""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


class PresetPanel(QWidget):
    """프리셋 주문 버튼 패널."""

    preset_clicked = Signal(str)  # preset_name

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
        title_label = QLabel("프리셋 주문")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)

        # 프리셋 버튼 컨테이너
        self.preset_container = QWidget()
        self.preset_layout = QVBoxLayout(self.preset_container)
        self.preset_layout.setSpacing(5)
        self.preset_layout.addStretch()

        scroll_area.setWidget(self.preset_container)
        layout.addWidget(scroll_area)

    def set_presets(self, presets: list[dict]) -> None:
        """프리셋 목록 설정."""
        # 기존 버튼 제거
        while self.preset_layout.count() > 1:  # stretch 제외
            item = self.preset_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 새 버튼 추가
        for preset in presets:
            name = preset.get("name", "Unknown")
            exchange = preset.get("exchange", "")
            market_id = preset.get("market_id", "")
            outcome = preset.get("outcome", "")
            side = preset.get("side", "")
            price = preset.get("price", 0.0)
            size = preset.get("size", 0.0)

            # 버튼 텍스트
            button_text = f"{name}\n{exchange} | {market_id[:20]}...\n{side} {outcome} @ {price} x {size}"
            button = QPushButton(button_text)
            button.setMinimumHeight(60)
            button.setStyleSheet(
                """
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """
            )
            button.clicked.connect(lambda checked, n=name: self.preset_clicked.emit(n))
            self.preset_layout.insertWidget(self.preset_layout.count() - 1, button)

    def clear(self) -> None:
        """프리셋 목록 초기화."""
        while self.preset_layout.count() > 1:
            item = self.preset_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

