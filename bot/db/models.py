from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from bot.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    
    # Settings
    show_images = Column(Boolean, default=True)
    show_reversed = Column(Boolean, default=True)
    daily_card_time = Column(String(8), default="09:00")
    timezone = Column(String(64), default="Europe/Moscow")
    notifications_enabled = Column(Boolean, default=True)
    
    # Daily limits - используем Text для JSON (SQLite не поддерживает JSON тип)
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
    
    def to_dict(self):
        """Convert user to dict"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "show_images": self.show_images,
            "show_reversed": self.show_reversed,
            "daily_card_time": self.daily_card_time,
            "timezone": self.timezone,
            "notifications_enabled": self.notifications_enabled,
            "usage_today": self.get_usage(),
            "last_reset_date": self.last_reset_date.isoformat() if self.last_reset_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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
    
    def to_dict(self):
        """Convert history to dict"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "spread_type": self.spread_type,
            "spread_data": self.get_spread_data(),
            "question": self.question,
            "image_path": self.image_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }