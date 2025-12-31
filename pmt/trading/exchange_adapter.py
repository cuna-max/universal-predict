"""dr-manhattan 거래소 어댑터."""

from datetime import datetime
from typing import Any, Optional

import dr_manhattan
from dr_manhattan.base.exchange import Exchange

from pmt.config.settings import Settings


class ExchangeAdapter:
    """dr-manhattan 거래소를 PMT에 맞게 래핑."""

    def __init__(self, settings: Settings) -> None:
        """초기화."""
        self.settings = settings
        self._exchanges: dict[str, Exchange] = {}

    def get_exchange(self, exchange_name: str) -> Optional[Exchange]:
        """거래소 인스턴스 가져오기 (캐싱)."""
        exchange_name_lower = exchange_name.lower()

        if exchange_name_lower in self._exchanges:
            print(f"[DEBUG] 거래소 {exchange_name} 캐시에서 반환")
            return self._exchanges[exchange_name_lower]

        try:
            config = self.settings.get_exchange_config(exchange_name_lower)
            print(f"[DEBUG] 거래소 {exchange_name} 초기화 시도, 설정 키: {list(config.keys())}")

            # DR_MANHATTAN.md에 따르면 create_exchange() 사용 권장
            if hasattr(dr_manhattan, "create_exchange"):
                exchange = dr_manhattan.create_exchange(exchange_name_lower, config)
            elif exchange_name_lower == "polymarket":
                exchange = dr_manhattan.Polymarket(config)
            elif exchange_name_lower == "opinion":
                exchange = dr_manhattan.Opinion(config)
            elif exchange_name_lower == "limitless":
                exchange = dr_manhattan.Limitless(config)
            else:
                raise ValueError(f"거래소 {exchange_name}를 생성할 수 없습니다.")

            print(f"[DEBUG] 거래소 {exchange_name} 초기화 성공, 타입: {type(exchange)}")
            self._exchanges[exchange_name_lower] = exchange
            return exchange
        except Exception as e:
            print(f"[ERROR] 거래소 초기화 실패 {exchange_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def list_available_exchanges(self) -> list[str]:
        """사용 가능한 거래소 목록 반환."""
        # DR_MANHATTAN.md에 따르면 list_exchanges() 함수가 있음
        try:
            # dr-manhattan의 list_exchanges 사용
            if hasattr(dr_manhattan, "list_exchanges"):
                exchanges = dr_manhattan.list_exchanges()
                print(f"[DEBUG] dr-manhattan.list_exchanges() 결과: {exchanges}")
                if exchanges:
                    return exchanges
        except Exception as e:
            print(f"[DEBUG] dr-manhattan.list_exchanges() 실패: {e}")

        # list_exchanges가 없는 경우, DR_MANHATTAN.md에 명시된 거래소 목록 사용
        # 문서: ['polymarket', 'limitless', 'opinion']
        known_exchanges = ["polymarket", "limitless", "opinion"]
        print(f"[DEBUG] 사용 가능한 거래소 (하드코딩): {known_exchanges}")
        return known_exchanges

    def get_all_exchanges(self) -> dict[str, Exchange]:
        """모든 거래소 인스턴스 반환."""
        available = self.list_available_exchanges()
        for name in available:
            self.get_exchange(name)
        return self._exchanges

    def fetch_markets(self, exchange_name: str) -> list[dict[str, Any]]:
        """
        거래소의 모든 마켓 데이터 조회.

        Args:
            exchange_name: 거래소 이름

        Returns:
            정규화된 마켓 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            print(f"[DEBUG] 거래소 {exchange_name} 인스턴스를 가져올 수 없습니다.")
            return []

        try:
            # 사용 가능한 메서드 확인
            available_methods = [m for m in dir(exchange) if not m.startswith("_")]
            print(f"[DEBUG] 거래소 {exchange_name} 사용 가능한 메서드: {available_methods[:10]}...")

            # DR_MANHATTAN.md: markets = polymarket.fetch_markets()
            # Market 객체 리스트 반환, market.question, market.prices 속성 있음
            if hasattr(exchange, "fetch_markets"):
                print(f"[DEBUG] {exchange_name}: fetch_markets() 호출 시도")
                markets = exchange.fetch_markets()
            else:
                print(f"[ERROR] 거래소 {exchange_name}에 fetch_markets() 메서드가 없습니다.")
                print(f"[DEBUG] 사용 가능한 메서드: {[m for m in available_methods if 'market' in m.lower()]}")
                return []

            if markets is None:
                print(f"[WARNING] {exchange_name}: 마켓 데이터가 None입니다.")
                return []

            print(f"[DEBUG] {exchange_name}: {len(markets) if isinstance(markets, (list, tuple)) else 'N/A'} 개 마켓 조회됨")

            # 정규화된 형식으로 변환
            normalized_markets = []
            for idx, market in enumerate(markets):
                try:
                    normalized = self._normalize_market_data(market, exchange_name)
                    if normalized:
                        normalized_markets.append(normalized)
                    else:
                        print(f"[WARNING] {exchange_name}: 마켓 {idx} 정규화 실패")
                except Exception as e:
                    print(f"[ERROR] {exchange_name}: 마켓 {idx} 정규화 중 오류: {e}")
                    import traceback
                    traceback.print_exc()

            print(f"[DEBUG] {exchange_name}: {len(normalized_markets)} 개 마켓 정규화 완료")
            return normalized_markets
        except Exception as e:
            print(f"[ERROR] 마켓 조회 실패 {exchange_name}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_market(self, exchange_name: str, market_id: str) -> Optional[dict[str, Any]]:
        """
        특정 마켓 상세 정보 조회.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID

        Returns:
            정규화된 마켓 데이터 또는 None
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return None

        try:
            # DR_MANHATTAN.md에는 fetch_market() 예제가 없지만, 일반적인 패턴
            # 먼저 fetch_markets()에서 해당 market_id 찾기 시도
            if hasattr(exchange, "fetch_market"):
                market = exchange.fetch_market(market_id)
            elif hasattr(exchange, "get_market"):
                market = exchange.get_market(market_id)
            else:
                # fetch_markets()에서 찾기
                print(f"[DEBUG] {exchange_name}: fetch_markets()에서 {market_id} 검색")
                markets = exchange.fetch_markets()
                for m in markets:
                    if self._get_market_id(m) == market_id:
                        return self._normalize_market_data(m, exchange_name)
                print(f"[WARNING] {exchange_name}: 마켓 {market_id}를 찾을 수 없습니다.")
                return None

            if not market:
                return None

            return self._normalize_market_data(market, exchange_name)
        except Exception as e:
            print(f"마켓 상세 조회 실패 {exchange_name}/{market_id}: {e}")
            return None

    def fetch_balance(self, exchange_name: str) -> Optional[float]:
        """
        거래소 계정 잔고 조회.

        Args:
            exchange_name: 거래소 이름

        Returns:
            잔고 (float) 또는 None
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            print(f"[DEBUG] 거래소 {exchange_name} 인스턴스를 가져올 수 없습니다.")
            return None

        try:
            # DR_MANHATTAN.md: balance = polymarket.fetch_balance()
            # dict 반환: {'USDC': ...}
            if hasattr(exchange, "fetch_balance"):
                print(f"[DEBUG] {exchange_name}: fetch_balance() 호출 시도")
                balance_dict = exchange.fetch_balance()
                print(f"[DEBUG] {exchange_name}: 잔고 조회 결과 = {balance_dict} (타입: {type(balance_dict)})")
                
                # dict에서 USDC 잔고 추출 (또는 첫 번째 값)
                if isinstance(balance_dict, dict):
                    # USDC 우선, 없으면 첫 번째 값
                    if "USDC" in balance_dict:
                        balance_value = balance_dict["USDC"]
                    elif balance_dict:
                        # 첫 번째 값 사용
                        balance_value = list(balance_dict.values())[0]
                    else:
                        print(f"[WARNING] {exchange_name}: 잔고 dict가 비어있습니다.")
                        return None
                    
                    try:
                        result = float(balance_value)
                        print(f"[DEBUG] {exchange_name}: 잔고 변환 성공 = {result}")
                        return result
                    except (ValueError, TypeError) as e:
                        print(f"[ERROR] 잔고 값 변환 실패 {exchange_name}: {balance_value} (오류: {e})")
                        return None
                else:
                    # dict가 아닌 경우 숫자로 변환 시도
                    try:
                        result = float(balance_dict)
                        return result
                    except (ValueError, TypeError):
                        print(f"[ERROR] {exchange_name}: 잔고가 예상 형식이 아닙니다: {type(balance_dict)}")
                        return None
            else:
                print(f"[ERROR] 거래소 {exchange_name}에 fetch_balance() 메서드가 없습니다.")
                return None
        except Exception as e:
            print(f"[ERROR] 잔고 조회 실패 {exchange_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_positions(self, exchange_name: str) -> list[dict[str, Any]]:
        """
        거래소의 모든 포지션 조회.

        Args:
            exchange_name: 거래소 이름

        Returns:
            정규화된 포지션 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return []

        try:
            # dr-manhattan API 호출
            if hasattr(exchange, "get_positions"):
                positions = exchange.get_positions()
            elif hasattr(exchange, "fetch_positions"):
                positions = exchange.fetch_positions()
            elif hasattr(exchange, "get_open_positions"):
                positions = exchange.get_open_positions()
            else:
                print(f"거래소 {exchange_name}에 포지션 조회 메서드가 없습니다.")
                return []

            if not positions:
                return []

            # 정규화된 형식으로 변환
            normalized_positions = []
            for position in positions:
                normalized = self._normalize_position_data(position, exchange_name)
                if normalized:
                    normalized_positions.append(normalized)

            return normalized_positions
        except Exception as e:
            print(f"포지션 조회 실패 {exchange_name}: {e}")
            return []

    def fetch_orders(self, exchange_name: str) -> list[dict[str, Any]]:
        """
        거래소의 모든 활성 주문 조회.

        Args:
            exchange_name: 거래소 이름

        Returns:
            정규화된 주문 데이터 리스트
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return []

        try:
            # dr-manhattan API 호출
            if hasattr(exchange, "get_orders"):
                orders = exchange.get_orders()
            elif hasattr(exchange, "fetch_orders"):
                orders = exchange.fetch_orders()
            elif hasattr(exchange, "get_open_orders"):
                orders = exchange.get_open_orders()
            else:
                print(f"거래소 {exchange_name}에 주문 조회 메서드가 없습니다.")
                return []

            if not orders:
                return []

            # 정규화된 형식으로 변환
            normalized_orders = []
            for order in orders:
                normalized = self._normalize_order_data(order, exchange_name)
                if normalized:
                    normalized_orders.append(normalized)

            return normalized_orders
        except Exception as e:
            print(f"주문 조회 실패 {exchange_name}: {e}")
            return []

    def cancel_order(self, exchange_name: str, order_id: str) -> tuple[bool, Optional[str]]:
        """
        주문 취소.

        Args:
            exchange_name: 거래소 이름
            order_id: 주문 ID

        Returns:
            (성공 여부, 에러 메시지)
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return False, f"거래소 {exchange_name}를 찾을 수 없습니다."

        try:
            # dr-manhattan API 호출
            if hasattr(exchange, "cancel_order"):
                result = exchange.cancel_order(order_id)
                # 결과가 bool이거나 dict일 수 있음
                if isinstance(result, bool):
                    return result, None if result else "주문 취소 실패"
                elif isinstance(result, dict):
                    success = result.get("success", False)
                    error = result.get("error")
                    return success, error
                else:
                    return True, None
            else:
                return False, f"거래소 {exchange_name}에 주문 취소 메서드가 없습니다."
        except Exception as e:
            error_msg = str(e)
            print(f"주문 취소 실패 {exchange_name}/{order_id}: {error_msg}")
            return False, error_msg

    def create_order(
        self,
        exchange_name: str,
        market_id: str,
        outcome: str,
        side: str,
        price: float,
        size: float,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        주문 생성.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID
            outcome: Yes 또는 No
            side: BUY 또는 SELL
            price: 가격
            size: 수량

        Returns:
            (성공 여부, order_id 또는 None, 에러 메시지 또는 None)
        """
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            return False, None, f"거래소 {exchange_name}를 찾을 수 없습니다."

        try:
            # dr-manhattan API 호출
            if hasattr(exchange, "create_order"):
                result = exchange.create_order(
                    market_id=market_id,
                    outcome=outcome,
                    side=side,
                    price=price,
                    size=size,
                )
                # 결과 형식에 따라 처리
                if isinstance(result, dict):
                    success = result.get("success", False)
                    order_id = result.get("order_id")
                    error = result.get("error")
                    return success, order_id, error
                elif isinstance(result, str):
                    # order_id만 반환하는 경우
                    return True, result, None
                else:
                    return True, None, None
            else:
                return False, None, f"거래소 {exchange_name}에 주문 생성 메서드가 없습니다."
        except Exception as e:
            error_msg = str(e)
            print(f"주문 생성 실패 {exchange_name}/{market_id}: {error_msg}")
            return False, None, error_msg

    def _normalize_market_data(self, market: Any, exchange_name: str) -> Optional[dict[str, Any]]:
        """
        마켓 데이터를 정규화된 형식으로 변환.

        Args:
            market: dr-manhattan 마켓 객체 또는 dict
            exchange_name: 거래소 이름

        Returns:
            정규화된 마켓 dict 또는 None
        """
        try:
            # dict인 경우 그대로 사용, 객체인 경우 dict로 변환 시도
            if isinstance(market, dict):
                market_dict = market
                print(f"[DEBUG] 마켓 데이터 타입: dict, 키: {list(market_dict.keys())[:10]}")
            elif hasattr(market, "__dict__"):
                market_dict = market.__dict__
                print(f"[DEBUG] 마켓 데이터 타입: 객체 (__dict__), 키: {list(market_dict.keys())[:10]}")
            elif hasattr(market, "to_dict"):
                market_dict = market.to_dict()
                print(f"[DEBUG] 마켓 데이터 타입: 객체 (to_dict), 키: {list(market_dict.keys())[:10]}")
            else:
                # DR_MANHATTAN.md: market.question, market.prices 속성 사용
                # Market 객체의 속성 직접 접근
                print(f"[DEBUG] 마켓 데이터 타입: 객체 (속성 접근), 사용 가능한 속성: {[a for a in dir(market) if not a.startswith('_')][:10]}")
                
                # prices는 dict일 수 있음 (예: {'Yes': 0.65, 'No': 0.35})
                prices = getattr(market, "prices", {})
                if isinstance(prices, dict):
                    yes_price = prices.get("Yes") or prices.get("yes")
                    no_price = prices.get("No") or prices.get("no")
                else:
                    yes_price = None
                    no_price = None
                
                market_dict = {
                    "market_id": getattr(market, "market_id", getattr(market, "id", "")),
                    "question": getattr(market, "question", getattr(market, "title", "")),
                    "yes_price": yes_price or getattr(market, "yes_price", getattr(market, "yesPrice", None)),
                    "no_price": no_price or getattr(market, "no_price", getattr(market, "noPrice", None)),
                    "volume": getattr(market, "volume", getattr(market, "totalVolume", 0.0)),
                    "close_time": getattr(market, "close_time", getattr(market, "closeTime", None)),
                    "status": getattr(market, "status", "open"),
                }

            # 정규화된 형식으로 변환
            # prices dict에서 추출한 경우도 처리
            yes_price = market_dict.get("yes_price")
            no_price = market_dict.get("no_price")
            
            # prices가 dict인 경우 다시 확인
            if isinstance(market_dict.get("prices"), dict):
                prices = market_dict.get("prices")
                yes_price = yes_price or prices.get("Yes") or prices.get("yes")
                no_price = no_price or prices.get("No") or prices.get("no")
            
            normalized = {
                "exchange": exchange_name,
                "market_id": market_dict.get("market_id") or market_dict.get("id", ""),
                "question": market_dict.get("question") or market_dict.get("title", ""),
                "yes_price": self._safe_float(yes_price),
                "no_price": self._safe_float(no_price),
                "volume": self._safe_float(market_dict.get("volume") or market_dict.get("totalVolume", 0.0)),
                "close_time": self._parse_datetime(
                    market_dict.get("close_time") or market_dict.get("closeTime")
                ),
                "status": market_dict.get("status", "open"),
            }

            # 필수 필드 검증
            if not normalized["market_id"]:
                print(f"[WARNING] 마켓 ID가 없습니다. 원본 데이터: {market_dict}")
                return None

            print(f"[DEBUG] 마켓 정규화 성공: {normalized['market_id'][:50]}...")
            return normalized
        except Exception as e:
            print(f"[ERROR] 마켓 데이터 정규화 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _normalize_position_data(self, position: Any, exchange_name: str) -> Optional[dict[str, Any]]:
        """
        포지션 데이터를 정규화된 형식으로 변환.

        Args:
            position: dr-manhattan 포지션 객체 또는 dict
            exchange_name: 거래소 이름

        Returns:
            정규화된 포지션 dict 또는 None
        """
        try:
            # dict인 경우 그대로 사용, 객체인 경우 dict로 변환 시도
            if isinstance(position, dict):
                pos_dict = position
            elif hasattr(position, "__dict__"):
                pos_dict = position.__dict__
            elif hasattr(position, "to_dict"):
                pos_dict = position.to_dict()
            else:
                pos_dict = {
                    "market_id": getattr(position, "market_id", getattr(position, "marketId", "")),
                    "outcome": getattr(position, "outcome", ""),
                    "size": getattr(position, "size", getattr(position, "quantity", 0.0)),
                    "avg_price": getattr(position, "avg_price", getattr(position, "averagePrice", 0.0)),
                }

            normalized = {
                "exchange": exchange_name,
                "market_id": pos_dict.get("market_id") or pos_dict.get("marketId", ""),
                "outcome": pos_dict.get("outcome", ""),
                "size": self._safe_float(pos_dict.get("size") or pos_dict.get("quantity", 0.0)),
                "avg_price": self._safe_float(
                    pos_dict.get("avg_price") or pos_dict.get("averagePrice", 0.0)
                ),
            }

            # 필수 필드 검증
            if not normalized["market_id"] or not normalized["outcome"]:
                return None

            return normalized
        except Exception as e:
            print(f"포지션 데이터 정규화 실패: {e}")
            return None

    def _normalize_order_data(self, order: Any, exchange_name: str) -> Optional[dict[str, Any]]:
        """
        주문 데이터를 정규화된 형식으로 변환.

        Args:
            order: dr-manhattan 주문 객체 또는 dict
            exchange_name: 거래소 이름

        Returns:
            정규화된 주문 dict 또는 None
        """
        try:
            # dict인 경우 그대로 사용, 객체인 경우 dict로 변환 시도
            if isinstance(order, dict):
                order_dict = order
            elif hasattr(order, "__dict__"):
                order_dict = order.__dict__
            elif hasattr(order, "to_dict"):
                order_dict = order.to_dict()
            else:
                order_dict = {
                    "market_id": getattr(order, "market_id", getattr(order, "marketId", "")),
                    "outcome": getattr(order, "outcome", ""),
                    "side": getattr(order, "side", ""),
                    "price": getattr(order, "price", 0.0),
                    "size": getattr(order, "size", getattr(order, "quantity", 0.0)),
                    "order_id": getattr(order, "order_id", getattr(order, "orderId", getattr(order, "id", ""))),
                }

            normalized = {
                "exchange": exchange_name,
                "market_id": order_dict.get("market_id") or order_dict.get("marketId", ""),
                "outcome": order_dict.get("outcome", ""),
                "side": order_dict.get("side", ""),
                "price": self._safe_float(order_dict.get("price", 0.0)),
                "size": self._safe_float(order_dict.get("size") or order_dict.get("quantity", 0.0)),
                "order_id": (
                    order_dict.get("order_id")
                    or order_dict.get("orderId")
                    or order_dict.get("id")
                    or ""
                ),
            }

            # 필수 필드 검증
            if not normalized["market_id"] or not normalized["order_id"]:
                return None

            return normalized
        except Exception as e:
            print(f"주문 데이터 정규화 실패: {e}")
            return None

    def _safe_float(self, value: Any) -> Optional[float]:
        """안전하게 float로 변환."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """안전하게 datetime으로 변환."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # ISO 형식 파싱 시도
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None

    def _get_market_id(self, market: Any) -> str:
        """마켓 객체에서 market_id 추출."""
        if isinstance(market, dict):
            return market.get("market_id") or market.get("id", "")
        return (
            getattr(market, "market_id", None)
            or getattr(market, "id", None)
            or ""
        )