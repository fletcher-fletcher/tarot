from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from bot.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)  # Меняем на BigInteger
    username = Column(String(128), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    
    # Settings
    show_images = Column(Boolean, default=True)
    show_reversed = Column(Boolean, default=True)
    daily_card_time = Column(String(8), default="09:00")
    timezone = Column(String(64), default="Europe/Moscow")
    notifications_enabled = Column(Boolean, default=True)
    
    # Daily limits - используем Text для JSON
    usage_today = Column(Text, default=json.dumps({"card_day": 0, "categories": 0}))
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")
    
    def get_usage(self):
        """Get usage as dict"""
        if isinstance(self.usage_today, str):
            return json.loads(self.usage_today)
        return self.usage_today or {"card_day": 0, "categories": 0}
    
    def set_usage(self, usage_dict):
        """Set usage from dict"""
        self.usage_today = json.dumps(usage_dict)


class History(Base):
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    spread_type = Column(String(64))
    spread_data = Column(Text, default=json.dumps([]))
    question = Column(Text, nullable=True)
    image_path = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="history")
    
    def get_spread_data(self):
        """Get spread data as dict"""
        if isinstance(self.spread_data, str):
            return json.loads(self.spread_data)
        return self.spread_data or []
    
    def set_spread_data(self, data):
        """Set spread data from dict"""
        self.spread_data = json.dumps(data)
