import os
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot/data/app.db")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    trial_started_at = Column(DateTime, default=datetime.utcnow)
    subscription_expires_at = Column(DateTime, nullable=True)


class SignalLog(Base):
    __tablename__ = "signal_logs"
    id = Column(Integer, primary_key=True)
    pair = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # BUY/SELL
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    os.makedirs("bot/data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_user_status(email: str) -> Dict[str, Any]:
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
        if user is None:
            user = User(email=email, is_active=True, trial_started_at=datetime.utcnow())
            session.add(user)
            session.commit()
            session.refresh(user)
        # 7-day trial logic
        trial_ends = user.trial_started_at + timedelta(days=7)
        subscribed = user.subscription_expires_at and user.subscription_expires_at > datetime.utcnow()
        blocked = (not subscribed) and (datetime.utcnow() > trial_ends)
        return {
            "email": user.email,
            "trial_ends_at": trial_ends.isoformat(),
            "subscribed": bool(subscribed),
            "blocked": bool(blocked)
        }


def get_admin_metrics() -> Dict[str, Any]:
    with SessionLocal() as session:
        total_users = session.query(User).count()
        total_signals = session.query(SignalLog).count()
        return {
            "total_users": total_users,
            "total_signals": total_signals
        }

