from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class URLMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)