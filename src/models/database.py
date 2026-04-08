"""SQLAlchemy database models for the traffic analyzer."""

import logging
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class TrafficRecord(Base):
    """Stores historical traffic condition snapshots."""

    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False, index=True)
    coordinates = Column(String(50), nullable=True)
    congestion_score = Column(Integer, nullable=False)
    congestion_level = Column(String(20), nullable=False)
    average_speed_kmh = Column(Float, nullable=True)
    incident_count = Column(Integer, default=0)
    road_conditions = Column(String(50), nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<TrafficRecord id={self.id} location={self.location!r} "
            f"congestion={self.congestion_score}>"
        )


class RouteRecord(Base):
    """Stores optimised route calculations."""

    __tablename__ = "route_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    distance_km = Column(Float, nullable=False)
    estimated_duration_min = Column(Float, nullable=False)
    congestion_factor = Column(Float, default=1.0)
    weather_delay_multiplier = Column(Float, default=1.0)
    calculated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<RouteRecord id={self.id} {self.start_location!r} -> "
            f"{self.end_location!r} {self.distance_km}km>"
        )


class AlertRecord(Base):
    """Stores traffic alert configurations and triggered alerts."""

    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    threshold = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    triggered = Column(Integer, default=0)  # 0=pending, 1=triggered, 2=resolved
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    triggered_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<AlertRecord id={self.id} location={self.location!r} "
            f"type={self.alert_type!r}>"
        )


class AnalysisRecord(Base):
    """Stores full AI-generated analysis results."""

    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    response = Column(Text, nullable=False)
    analysis_type = Column(String(50), default="general")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return f"<AnalysisRecord id={self.id} type={self.analysis_type!r}>"


def init_db(database_url: str) -> sessionmaker:
    """Initialise the database and return a session factory.

    Args:
        database_url: SQLAlchemy connection string.

    Returns:
        Configured ``sessionmaker`` instance.
    """
    logger.info("Initialising database: %s", database_url)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db(session_factory: sessionmaker):
    """Yield a database session (for use as a FastAPI dependency).

    Args:
        session_factory: The ``sessionmaker`` returned by ``init_db``.
    """
    db: Session = session_factory()
    try:
        yield db
    finally:
        db.close()
