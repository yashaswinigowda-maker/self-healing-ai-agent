from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.db_models import (
        TaskRecord,
        TaskStepRecord,
        RecoveryAttemptRecord,
        VerificationRecord,
        FailurePredictionRecord,
        MemoryRecord
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized.")
