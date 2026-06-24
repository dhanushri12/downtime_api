#═══════════════════════════════════════════════════════════════════════
#DATABASE MODULE
#═══════════════════════════════════════════════════════════════════════

from typing import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session  # ← Only import once
from sqlalchemy.pool import QueuePool

from config import settings

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# DATABASE ENGINE CREATION
# ═══════════════════════════════════════════════
try:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

# ═══════════════════════════════════════════════
# SESSION FACTORY
# ═══════════════════════════════════════════════
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# ═══════════════════════════════════════════════
# BASE CLASS FOR ALL MODELS
# ═══════════════════════════════════════════════
Base = declarative_base()

# ═══════════════════════════════════════════════
# DATABASE DEPENDENCY INJECTION
# ═══════════════════════════════════════════════

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# ═══════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════
def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# ═══════════════════════════════════════════════
# CONNECTION TESTING
# ═══════════════════════════════════════════════
def test_db_connection() -> bool:
    try:
        with engine.connect() as connection:
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False