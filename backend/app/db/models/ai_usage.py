from sqlalchemy import BigInteger, Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class AiUsageLog(Base):
    __tablename__ = "ai_usage_log"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    purpose = Column(String(20), nullable=False)
    provider = Column(String(20), nullable=False)
    model = Column(String(80), nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    outcome = Column(String(20), nullable=False)

    __table_args__ = (
        Index("ai_usage_recent_idx", created_at.desc()),
        Index("ai_usage_user_recent_idx", user_id, created_at.desc()),
    )
