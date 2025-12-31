# 개발 가이드

## 초기 설정

### 1. 가상 환경 생성 및 활성화

```bash
# uv 사용 (권장)
uv venv
source .venv/bin/activate  # Linux/Mac
# 또는 .venv\Scripts\activate  # Windows

# 또는 pip 사용
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
# 개발 의존성 포함 설치
uv pip install -e ".[dev]"

# 또는 pip 사용
pip install -e ".[dev]"
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성 (수동으로 생성 필요)
cp .env.example .env

# .env 파일 편집하여 거래소 인증 정보 입력
# 주의: 실제 거래 시에만 private_key 입력, 테스트 시에는 비워둠
```

### 4. 데이터베이스 초기화

애플리케이션 실행 시 자동으로 `data/pmt.db` 파일이 생성됩니다.

## 개발 워크플로우

### 코드 실행

```bash
# 개발 모드 실행
python -m pmt.main

# 또는 설치 후
pmt
```

### 코드 포맷팅

```bash
# Black으로 포맷팅
black pmt/

# Ruff로 린팅
ruff check pmt/
ruff check --fix pmt/  # 자동 수정
```

### 타입 체크

```bash
mypy pmt/
```

### 테스트 실행

```bash
pytest tests/
```

## 프로젝트 구조 이해

자세한 내용은 [ARCHITECTURE.md](./ARCHITECTURE.md)를 참고하세요.

### 주요 모듈

- **pmt/main.py**: 애플리케이션 진입점
- **pmt/ui/**: PySide6 기반 UI 컴포넌트
- **pmt/core/**: 비즈니스 로직 및 도메인 규칙
- **pmt/trading/**: dr-manhattan 거래소 어댑터
- **pmt/storage/**: SQLite 데이터베이스 관리
- **pmt/config/**: 설정 및 프리셋 관리

## 새 기능 추가 가이드

### 1. 새 UI 컴포넌트 추가

```python
# pmt/ui/new_component.py
from PySide6.QtWidgets import QWidget

class NewComponent(QWidget):
    def __init__(self):
        super().__init__()
        # 구현
```

### 2. 새 비즈니스 로직 추가

```python
# pmt/core/new_manager.py
class NewManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        # 구현
```

### 3. 새 데이터 모델 추가

```python
# pmt/storage/models.py에 추가
class NewModel(Base):
    __tablename__ = "new_table"
    # 컬럼 정의
```

## 디버깅

### 로그 확인

주문 로그는 SQLite 데이터베이스에 저장됩니다:

```python
from pmt.storage.database import Database
from pmt.storage.models import OrderLog

db = Database(Path("data/pmt.db"))
session = db.get_session()
logs = session.query(OrderLog).all()
```

### Dry Run 모드

기본적으로 Dry Run 모드가 활성화되어 있어 실제 주문이 실행되지 않습니다.
실제 주문을 테스트하려면 `.env`에서 `DRY_RUN_MODE=false`로 설정하세요.

## 빌드 및 배포

### PyInstaller로 단일 실행파일 생성

```bash
# 빌드 스크립트 (추후 추가 예정)
pyinstaller --onefile --windowed pmt/main.py
```

## 문제 해결

### dr-manhattan 설치 오류

```bash
# dr-manhattan이 PyPI에 없다면 GitHub에서 직접 설치
pip install git+https://github.com/guzus/dr-manhattan.git
```

### PySide6 설치 오류

```bash
# Qt 의존성 문제 시
pip install --upgrade pip
pip install PySide6
```

### 데이터베이스 잠금 오류

SQLite 파일이 다른 프로세스에 의해 잠겨있을 수 있습니다.
애플리케이션을 모두 종료한 후 다시 시도하세요.

## 참고 자료

- [dr-manhattan 문서](https://github.com/guzus/dr-manhattan)
- [PySide6 문서](https://doc.qt.io/qtforpython/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
