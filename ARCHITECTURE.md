# PMT 아키텍처 문서

## 프로젝트 구조

```
pmt/
├── pmt/                    # 메인 패키지
│   ├── __init__.py
│   ├── main.py            # 애플리케이션 진입점
│   │
│   ├── ui/                # UI 레이어 (PySide6)
│   │   ├── __init__.py
│   │   ├── main_window.py        # 메인 윈도우
│   │   ├── market_board.py       # 통합 마켓 보드 (TODO)
│   │   ├── market_detail.py      # 마켓 상세 패널 (TODO)
│   │   ├── preset_panel.py       # 프리셋 주문 패널 (TODO)
│   │   ├── account_panel.py       # 계정/포지션 패널 (TODO)
│   │   └── widgets/              # 재사용 가능한 위젯
│   │       └── __init__.py
│   │
│   ├── core/              # 비즈니스 로직 레이어
│   │   ├── __init__.py
│   │   ├── market_manager.py     # 마켓 데이터 관리 (TODO)
│   │   ├── preset_manager.py     # 프리셋 관리 (TODO)
│   │   └── risk_guard.py         # 리스크 가드 시스템
│   │
│   ├── trading/           # 거래 엔진 레이어
│   │   ├── __init__.py
│   │   ├── exchange_adapter.py   # dr-manhattan 어댑터
│   │   └── order_executor.py     # 주문 실행기 (TODO)
│   │
│   ├── storage/           # 저장소 레이어
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite 관리
│   │   └── models.py            # 데이터베이스 모델
│   │
│   └── config/            # 설정 관리 레이어
│       ├── __init__.py
│       ├── settings.py          # 전역 설정
│       └── preset_loader.py     # YAML 프리셋 로더
│
├── presets/               # YAML 프리셋 파일들
│   └── default.yaml
│
├── data/                  # SQLite DB 저장 위치
│   └── pmt.db
│
├── tests/                 # 테스트
│   └── __init__.py
│
├── pyproject.toml         # 프로젝트 설정 및 의존성
├── README.md              # 프로젝트 개요
├── SPECIFICATION.md       # 제품 기획서
└── ARCHITECTURE.md        # 이 문서
```

## 레이어 아키텍처

### 1. UI 레이어 (`pmt/ui/`)

**책임**: 사용자 인터페이스 및 사용자 상호작용 처리

- **main_window.py**: 메인 윈도우 및 레이아웃 관리
- **market_board.py**: 통합 마켓 보드 (테이블 뷰)
- **market_detail.py**: 선택된 마켓 상세 정보 표시
- **preset_panel.py**: 프리셋 주문 버튼 및 실행 UI
- **account_panel.py**: 잔고, 포지션, 활성 주문 표시

**의존성**: `core/`, `trading/`, `config/`

### 2. Core 레이어 (`pmt/core/`)

**책임**: 비즈니스 로직 및 도메인 규칙

- **market_manager.py**: 마켓 데이터 캐싱, 필터링, 갱신 관리
- **preset_manager.py**: 프리셋 로드, 검증, 실행 흐름 관리
- **risk_guard.py**: 주문 실행 전 리스크 검증

**의존성**: `config/`, `storage/`

### 3. Trading 레이어 (`pmt/trading/`)

**책임**: 거래소 통신 및 주문 실행

- **exchange_adapter.py**: dr-manhattan 거래소 인스턴스 관리
- **order_executor.py**: 주문 실행, 취소, 상태 추적

**의존성**: `dr-manhattan`, `core/`, `storage/`

### 4. Storage 레이어 (`pmt/storage/`)

**책임**: 데이터 영속성 관리

- **database.py**: SQLite 연결 및 세션 관리
- **models.py**: 데이터베이스 모델 정의 (OrderLog, MarketCache 등)

**의존성**: 없음 (독립적)

### 5. Config 레이어 (`pmt/config/`)

**책임**: 설정 및 프리셋 관리

- **settings.py**: 환경 변수 로드 및 전역 설정
- **preset_loader.py**: YAML 프리셋 파일 파싱

**의존성**: 없음 (독립적)

## 데이터 흐름

### 마켓 데이터 로딩

```
UI (market_board) 
  → Core (market_manager) 
    → Trading (exchange_adapter) 
      → dr-manhattan (fetch_markets)
        → Storage (market_cache 저장)
          → UI (테이블 업데이트)
```

### 프리셋 주문 실행

```
UI (preset_panel) 
  → Core (preset_manager)
    → Core (risk_guard) [검증]
      → UI (확인 모달)
        → Trading (order_executor)
          → Trading (exchange_adapter)
            → dr-manhattan (create_order)
              → Storage (order_log 저장)
                → UI (결과 표시)
```

## 주요 설계 원칙

### 1. Exchange-agnostic

- 모든 거래소는 `dr-manhattan`의 표준 `Exchange` 인터페이스를 통해 접근
- `ExchangeAdapter`가 거래소별 차이를 추상화

### 2. Local-first

- 모든 데이터는 로컬 SQLite에 저장
- 네트워크 요청은 최소화하고 캐싱 활용

### 3. Risk-first

- 모든 주문은 `RiskGuard`를 통과해야 함
- Dry Run 모드가 기본값

### 4. Preset-driven

- 수동 입력 대신 YAML로 정의된 프리셋 사용
- 프리셋은 검증된 매크로 역할

## 의존성 관리

### 외부 라이브러리

- **dr-manhattan**: 예측시장 거래소 통합 API
- **PySide6**: Qt 기반 GUI 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **PyYAML**: 프리셋 파일 파싱
- **python-dotenv**: 환경 변수 관리

### 내부 의존성 방향

```
UI → Core → Trading → dr-manhattan
  ↘      ↘ Storage
    Config
```

- 상위 레이어는 하위 레이어에만 의존
- Config와 Storage는 독립적
- 순환 의존성 없음

## 확장성

### 새로운 거래소 추가

1. `dr-manhattan`에 거래소 추가 (PMT 코드 변경 불필요)
2. `ExchangeAdapter`가 자동으로 감지하여 사용 가능

### 새로운 기능 추가

- **UI 기능**: `ui/` 하위에 새 위젯 추가
- **비즈니스 로직**: `core/` 하위에 새 매니저 추가
- **데이터 모델**: `storage/models.py`에 새 모델 추가

## 보안 고려사항

1. **Private Key**: `.env` 파일에 저장, Git에 커밋하지 않음
2. **Dry Run 모드**: 기본값으로 실제 주문 차단
3. **Market Allowlist**: 프리셋에 정의된 마켓만 주문 가능
4. **로컬 전용**: 네트워크 서버 없음, 모든 데이터 로컬 저장

## 성능 최적화

1. **마켓 캐싱**: SQLite에 캐시하여 중복 요청 방지
2. **병렬 로딩**: 여러 거래소 마켓 데이터 병렬 로드
3. **지연 로딩**: 거래소 인스턴스는 필요 시에만 생성

## 테스트 전략

- **Unit Tests**: 각 레이어별 독립 테스트
- **Integration Tests**: 레이어 간 통합 테스트
- **UI Tests**: pytest-qt를 사용한 UI 테스트

