"""PMT 메인 진입점."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pmt.config.settings import Settings
from pmt.ui.main_window import MainWindow


def main() -> None:
    """애플리케이션 진입점."""
    app = QApplication(sys.argv)
    app.setApplicationName("Prediction Market Terminal")
    app.setOrganizationName("PMT")

    # 설정 로드
    settings = Settings()

    # 메인 윈도우 생성 및 표시
    window = MainWindow(settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

