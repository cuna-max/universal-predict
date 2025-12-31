"""데이터베이스 모델."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from pmt.storage.database import Base


class OrderLog(Base):
    """주문 로그 모델."""

    __tablename__ = "order_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    exchange = Column(String(50), nullable=False)
    market_id = Column(String(200), nullable=False)
    outcome = Column(String(10), nullable=False)
    side = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    order_id = Column(String(200), nullable=True)
    status = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    preset_name = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        """문자열 표현."""
        return (
            f"<OrderLog(id={self.id}, exchange={self.exchange}, "
            f"market_id={self.market_id}, status={self.status})>"
        )


class MarketCache(Base):
    """마켓 데이터 캐시 모델."""

    __tablename__ = "market_cache"

    id = Column(Integer, primary_key=True)
    exchange = Column(String(50), nullable=False)
    market_id = Column(String(200), nullable=False, unique=True)
    question = Column(Text, nullable=False)
    yes_price = Column(Float, nullable=True)
    no_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    close_time = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        """문자열 표현."""
        return (
            f"<MarketCache(exchange={self.exchange}, "
            f"market_id={self.market_id}, question={self.question[:50]}...)>"
        )

