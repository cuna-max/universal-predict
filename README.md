# Prediction Market Terminal (PMT)

dr-manhattan 기반 개인용 예측시장 통합 트레이딩 터미널

## 개요

PMT는 Polymarket, Opinion, Limitless 등 여러 예측 시장을 단일 화면에서 통합 조회하고, 미리 정의된 "프리셋 주문"으로 즉시 진입할 수 있도록 설계된 로컬 전용 트레이딩 애플리케이션입니다.

## 주요 특징

- **Local-first**: 모든 키, 주문, 로그는 로컬에서만 관리
- **Exchange-agnostic**: dr-manhattan 표준 API를 통한 거래소 추상화
- **Preset-driven**: 수동 입력이 아닌 사전 정의된 매매 매크로 구조
- **Risk-first**: 실주문보다 리스크 가드가 우선

## 개발 환경 설정

### 요구사항

- Python >= 3.11
- uv (권장) 또는 pip

### 설치

```bash
# uv 사용 (권장)
uv venv
source .venv/bin/activate  # Linux/Mac
# 또는 .venv\Scripts\activate  # Windows

uv pip install -e ".[dev]"

# 또는 pip 사용
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 거래소 인증 정보 입력
```

## 실행

```bash
# 개발 모드
python -m pmt.main

# 또는 설치 후
pmt
```

## 프로젝트 구조

```
pmt/
├── pmt/                    # 메인 패키지
│   ├── ui/                # UI 레이어 (PySide6)
│   ├── core/              # 비즈니스 로직
│   ├── trading/           # 거래 엔진 (dr-manhattan 래퍼)
│   ├── storage/           # 저장소 (SQLite)
│   └── config/            # 설정 관리
├── presets/               # YAML 프리셋 파일들
├── data/                  # SQLite DB 저장 위치
└── tests/                 # 테스트
```

## 개발 가이드

자세한 내용은 [SPECIFICATION.md](./SPECIFICATION.md)를 참고하세요.

## 라이선스

MIT

