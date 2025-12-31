"""마켓 데이터 관리자."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from pmt.config.settings import Settings
from pmt.storage.database import Database
from pmt.storage.models import MarketCache
from pmt.trading.exchange_adapter import ExchangeAdapter


class MarketManager(QObject):
    """마켓 데이터 로딩 및 캐싱 관리."""

    markets_loaded = Signal(list)  # 정규화된 마켓 데이터 리스트
    loading_started = Signal()
    loading_finished = Signal()

    def __init__(self, settings: Settings, exchange_adapter: ExchangeAdapter, database: Database) -> None:
        """초기화."""
        super().__init__()
        self.settings = settings
        self.exchange_adapter = exchange_adapter
        self.database = database
        self.executor = ThreadPoolExecutor(max_workers=5)

    def load_all_markets(self, use_cache: bool = True) -> None:
        """
        모든 거래소의 마켓 데이터 병렬 로딩.

        Args:
            use_cache: 캐시 사용 여부
        """
        self.loading_started.emit()

        def _load():
            all_markets = []
            cache_valid = use_cache and self._is_cache_valid()

            if cache_valid:
                # 캐시에서 로드
                markets = self._load_from_cache()
                if markets:
                    self.markets_loaded.emit(markets)
                    self.loading_finished.emit()
                    return

            # 실제 API 호출
            available_exchanges = self.exchange_adapter.list_available_exchanges()
            print(f"[DEBUG] MarketManager: 사용 가능한 거래소 {len(available_exchanges)}개: {available_exchanges}")
            
            if not available_exchanges:
                print("[WARNING] MarketManager: 사용 가능한 거래소가 없습니다.")
                self.markets_loaded.emit([])
                self.loading_finished.emit()
                return

            futures = {}

            for exchange_name in available_exchanges:
                print(f"[DEBUG] MarketManager: {exchange_name} 마켓 로딩 시작")
                future = self.executor.submit(self.exchange_adapter.fetch_markets, exchange_name)
                futures[future] = exchange_name

            for future in as_completed(futures):
                exchange_name = futures[future]
                try:
                    markets = future.result()
                    print(f"[DEBUG] MarketManager: {exchange_name}에서 {len(markets)}개 마켓 로드됨")
                    all_markets.extend(markets)
                except Exception as e:
                    print(f"[ERROR] 마켓 로딩 실패 {exchange_name}: {e}")
                    import traceback
                    traceback.print_exc()

            print(f"[DEBUG] MarketManager: 총 {len(all_markets)}개 마켓 로드 완료")

            # 캐시 저장
            if all_markets:
                self._save_to_cache(all_markets)
                print(f"[DEBUG] MarketManager: {len(all_markets)}개 마켓 캐시 저장 완료")

            self.markets_loaded.emit(all_markets)
            self.loading_finished.emit()

        # 백그라운드 스레드에서 실행
        self.executor.submit(_load)

    def _is_cache_valid(self) -> bool:
        """캐시 유효성 검사."""
        try:
            session = self.database.get_session()
            try:
                # 가장 최근 캐시 확인
                latest_cache = (
                    session.query(MarketCache)
                    .order_by(MarketCache.cached_at.desc())
                    .first()
                )
                if not latest_cache:
                    return False

                cache_age = datetime.utcnow() - latest_cache.cached_at
                return cache_age.total_seconds() < self.settings.cache_refresh_interval
            finally:
                session.close()
        except Exception as e:
            print(f"캐시 유효성 검사 실패: {e}")
            return False

    def _load_from_cache(self) -> list[dict[str, Any]]:
        """캐시에서 마켓 데이터 로드."""
        try:
            session = self.database.get_session()
            try:
                cached_markets = session.query(MarketCache).all()
                markets = []
                for cache in cached_markets:
                    market = {
                        "exchange": cache.exchange,
                        "market_id": cache.market_id,
                        "question": cache.question,
                        "yes_price": cache.yes_price,
                        "no_price": cache.no_price,
                        "volume": cache.volume,
                        "close_time": cache.close_time,
                        "status": cache.status,
                    }
                    markets.append(market)
                return markets
            finally:
                session.close()
        except Exception as e:
            print(f"캐시 로드 실패: {e}")
            return []

    def _save_to_cache(self, markets: list[dict[str, Any]]) -> None:
        """마켓 데이터를 캐시에 저장."""
        try:
            session = self.database.get_session()
            try:
                # 기존 캐시 삭제
                session.query(MarketCache).delete()

                # 새 캐시 저장
                for market in markets:
                    cache = MarketCache(
                        exchange=market.get("exchange", ""),
                        market_id=market.get("market_id", ""),
                        question=market.get("question", ""),
                        yes_price=market.get("yes_price"),
                        no_price=market.get("no_price"),
                        volume=market.get("volume"),
                        close_time=market.get("close_time"),
                        status=market.get("status", "open"),
                        cached_at=datetime.utcnow(),
                    )
                    session.add(cache)

                session.commit()
            except Exception as e:
                session.rollback()
                print(f"캐시 저장 실패: {e}")
            finally:
                session.close()
        except Exception as e:
            print(f"캐시 저장 오류: {e}")

    def get_market(self, exchange_name: str, market_id: str) -> Optional[dict[str, Any]]:
        """
        특정 마켓 상세 정보 조회.

        Args:
            exchange_name: 거래소 이름
            market_id: 마켓 ID

        Returns:
            마켓 데이터 또는 None
        """
        return self.exchange_adapter.fetch_market(exchange_name, market_id)

    def shutdown(self) -> None:
        """리소스 정리."""
        self.executor.shutdown(wait=True)

