"""마켓 상세 정보 패널."""

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MarketDetailPanel(QWidget):
    """선택된 마켓의 상세 정보를 표시하는 패널."""

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
        title_label = QLabel("마켓 상세 정보")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 질문
        question_label = QLabel("질문:")
        question_label.setStyleSheet("font-weight: bold;")
        self.question_text = QLabel("마켓을 선택하세요")
        self.question_text.setWordWrap(True)
        self.question_text.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(question_label)
        layout.addWidget(self.question_text)

        # Outcome View
        outcome_label = QLabel("가격:")
        outcome_label.setStyleSheet("font-weight: bold;")
        self.outcome_text = QLabel("YES: - | NO: -")
        self.outcome_text.setStyleSheet("padding: 5px; background-color: #e8f4f8; border-radius: 3px;")
        layout.addWidget(outcome_label)
        layout.addWidget(self.outcome_text)

        # 마감 시간
        close_label = QLabel("마감 시간:")
        close_label.setStyleSheet("font-weight: bold;")
        self.close_text = QLabel("-")
        self.close_text.setStyleSheet("padding: 5px;")
        layout.addWidget(close_label)
        layout.addWidget(self.close_text)

        # 포지션 요약
        position_label = QLabel("보유 포지션:")
        position_label.setStyleSheet("font-weight: bold;")
        self.position_text = QLabel("없음")
        self.position_text.setStyleSheet("padding: 5px; background-color: #fff4e6; border-radius: 3px;")
        layout.addWidget(position_label)
        layout.addWidget(self.position_text)

        # 스페이서
        layout.addStretch()

    def set_market(self, market_data: dict) -> None:
        """마켓 데이터 설정."""
        # 질문
        question = market_data.get("question", "N/A")
        self.question_text.setText(question)

        # 가격
        yes_price = market_data.get("yes_price", 0.0)
        no_price = market_data.get("no_price", 0.0)
        spread = abs(yes_price + no_price - 1.0) if yes_price and no_price else 0.0
        price_text = f"YES: {yes_price:.3f} | NO: {no_price:.3f}"
        if spread > 0:
            price_text += f" | Spread: {spread:.3f}"
        self.outcome_text.setText(price_text)

        # 마감 시간
        close_time = market_data.get("close_time")
        if close_time:
            if isinstance(close_time, datetime):
                close_str = close_time.strftime("%Y-%m-%d %H:%M:%S")
                # 카운트다운 계산
                now = datetime.now()
                if close_time > now:
                    delta = close_time - now
                    days = delta.days
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    countdown = f"{days}일 {hours}시간 {minutes}분 남음"
                    close_str += f" ({countdown})"
            else:
                close_str = str(close_time)
        else:
            close_str = "N/A"
        self.close_text.setText(close_str)

        # 포지션 (임시로 없음 표시, 나중에 실제 데이터 연결)
        position = market_data.get("position", None)
        if position:
            self.position_text.setText(f"YES: {position.get('yes', 0)}, NO: {position.get('no', 0)}")
        else:
            self.position_text.setText("없음")

    def clear(self) -> None:
        """마켓 정보 초기화."""
        self.question_text.setText("마켓을 선택하세요")
        self.outcome_text.setText("YES: - | NO: -")
        self.close_text.setText("-")
        self.position_text.setText("없음")

