# Prediction Market Terminal (PMT) – Product Specification v1.0

> dr-manhattan 기반  
> 개인용 예측시장 통합 트레이딩 터미널

---

## 1. Product Vision

**Prediction Market Terminal(PMT)**은 Polymarket, Opinion, Limitless 등
여러 예측 시장을 단일 화면에서 통합 조회하고,
미리 정의된 “프리셋 주문”으로 즉시 진입할 수 있도록 설계된
**로컬 전용 트레이딩 애플리케이션**이다.

본 제품은 웹 서비스가 아닌,
**개인 트레이더의 실행 단말(Terminal)** 개념으로 설계되며
서버, 계정 공유, 클라우드 저장을 일절 사용하지 않는다.

---

## 2. Design Principles

| 원칙              | 설명                                          |
| ----------------- | --------------------------------------------- |
| Local-first       | 모든 키, 주문, 로그는 로컬에서만 관리         |
| Exchange-agnostic | dr-manhattan 표준 API를 통한 거래소 추상화    |
| Preset-driven     | 수동 입력이 아닌 사전 정의된 매매 매크로 구조 |
| Risk-first        | 실주문보다 리스크 가드가 우선                 |
| Deterministic     | 항상 동일한 프리셋 → 동일한 결과              |

---

## 3. Supported Markets

PMT는 dr-manhattan이 지원하는 모든 예측시장 거래소를 자동 감지하여 로딩한다.

- Polymarket
- Opinion
- Limitless
- (향후 dr-manhattan 추가 거래소 자동 호환)

---

## 4. Core Features

### 4.1 Unified Market Board

| 항목           | 설명                                                     |
| -------------- | -------------------------------------------------------- |
| Market Loading | 모든 거래소 `fetch_markets()` 병렬 로딩                  |
| View           | 테이블 기반 단일 뷰                                      |
| Data           | Question / YES / NO Price / Volume / Close Time / Status |
| Filters        | Keyword / Close Time / Volume / Status                   |
| Refresh        | 10–30초 캐시 기반 자동 갱신                              |

---

### 4.2 Market Detail Panel

| 기능             | 내용                       |
| ---------------- | -------------------------- |
| Question         | 전체 질문 원문 표시        |
| Outcome View     | Yes/No 가격, Spread 표시   |
| Close Time       | 마감 카운트다운            |
| Position Summary | 해당 마켓 보유 포지션 표시 |

---

### 4.3 Preset Order System

#### Preset Definition (YAML)

```yaml
- name: FED_YES_SMALL
  exchange: polymarket
  market_id: fed-2026-rate
  outcome: Yes
  side: BUY
  price: 0.64
  size: 50
```

| 속성      | 설명              |
| --------- | ----------------- |
| name      | UI 버튼 표시 이름 |
| exchange  | 대상 거래소       |
| market_id | 주문 허용 마켓    |
| outcome   | Yes / No          |
| side      | BUY / SELL        |
| price     | 지정가            |
| size      | 수량              |

#### Preset Execution Flow

1. Preset 선택
2. Risk Precheck 수행
3. 2-step Confirm Modal 표시
4. `create_order()` 실행

---

### 4.4 Risk Guard System

| Rule             | Description                      |
| ---------------- | -------------------------------- |
| Dry Run Mode     | 기본 ON, 실제 주문 차단          |
| Market Allowlist | Preset에 정의된 마켓만 주문 가능 |
| Max Notional     | price × size 상한 제한           |
| Max Size         | 수량 상한 제한                   |
| Double Confirm   | 실주문 전 2회 확인               |
| Error Shield     | 잔고 부족, 가격 오류 자동 차단   |

---

### 4.5 Account & Position Panel

| 항목        | 내용               |
| ----------- | ------------------ |
| Balance     | 거래소별 잔고 조회 |
| Positions   | 시장별 포지션      |
| Open Orders | 활성 주문 리스트   |
| Cancel      | 주문 취소 지원     |

---

## 5. Technical Architecture

| Layer          | Stack        |
| -------------- | ------------ |
| UI             | PySide6 (Qt) |
| Core           | Python 3.11  |
| Trading Engine | dr-manhattan |
| Presets        | YAML         |
| Storage        | SQLite       |
| Packaging      | PyInstaller  |

---

## 6. Storage & Security

| Item         | Policy             |
| ------------ | ------------------ |
| Private Keys | `.env` 로컬 저장   |
| Logs         | SQLite local DB    |
| Network      | No external server |
| Backup       | User local only    |

---

## 7. Non-Goals / Restrictions

| 항목            | 제한             |
| --------------- | ---------------- |
| Manual Trading  | ❌ 지원하지 않음 |
| Cloud Sync      | ❌               |
| Account Sharing | ❌               |
| Signal Provider | ❌               |
| Copy Trading    | ❌               |

---

## 8. MVP Completion Criteria

- 모든 거래소 자동 로딩 성공
- Preset 주문 실제 체결 가능
- Risk Guard 전 항목 정상 동작
- 단일 실행파일 배포 성공
