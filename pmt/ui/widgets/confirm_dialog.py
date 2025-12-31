"""주문 확인 다이얼로그."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ConfirmDialog(QDialog):
    """2-step 확인 다이얼로그."""

    def __init__(self, preset_data: dict, dry_run_mode: bool, parent: Optional[QWidget] = None) -> None:
        """
        초기화.

        Args:
            preset_data: 프리셋 데이터
            dry_run_mode: Dry Run 모드 여부
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.preset_data = preset_data
        self.dry_run_mode = dry_run_mode
        self._step = 1
        self._init_ui()

    def _init_ui(self) -> None:
        """UI 초기화."""
        self.setWindowTitle("주문 확인")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 프리셋 정보 표시
        info_label = QLabel(self._format_preset_info())
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)

        # Dry Run 모드 표시
        if self.dry_run_mode:
            dry_run_label = QLabel("⚠️ Dry Run 모드: 실제 주문이 실행되지 않습니다")
            dry_run_label.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            layout.addWidget(dry_run_label)

        # 확인 메시지
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.message_label)

        # 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("확인")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        button_box.accepted.connect(self._on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self._update_message()

    def _format_preset_info(self) -> str:
        """프리셋 정보 포맷팅."""
        name = self.preset_data.get("name", "Unknown")
        exchange = self.preset_data.get("exchange", "")
        market_id = self.preset_data.get("market_id", "")
        outcome = self.preset_data.get("outcome", "")
        side = self.preset_data.get("side", "")
        price = self.preset_data.get("price", 0.0)
        size = self.preset_data.get("size", 0.0)

        return (
            f"<b>프리셋:</b> {name}<br/>"
            f"<b>거래소:</b> {exchange}<br/>"
            f"<b>마켓:</b> {market_id}<br/>"
            f"<b>Outcome:</b> {outcome}<br/>"
            f"<b>Side:</b> {side}<br/>"
            f"<b>가격:</b> {price:.4f}<br/>"
            f"<b>수량:</b> {size:.2f}<br/>"
            f"<b>총액:</b> {price * size:.2f}"
        )

    def _update_message(self) -> None:
        """메시지 업데이트."""
        if self._step == 1:
            self.message_label.setText("주문을 실행하시겠습니까?")
        else:
            self.message_label.setText("정말 실행하시겠습니까? (최종 확인)")

    def _on_ok_clicked(self) -> None:
        """확인 버튼 클릭."""
        if self._step == 1:
            # 1단계: 2단계로 진행
            self._step = 2
            self._update_message()
        else:
            # 2단계: 확인 완료
            self.accept()

    @staticmethod
    def show_confirmation(preset_data: dict, dry_run_mode: bool, parent: Optional[QWidget] = None) -> bool:
        """
        확인 다이얼로그 표시.

        Returns:
            확인 여부
        """
        dialog = ConfirmDialog(preset_data, dry_run_mode, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted

