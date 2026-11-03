# database/infrastructure/database/init.py
import logging
import time

from sqlalchemy.exc import DBAPIError

from database.infrastructure.database.connection import engine
from database.infrastructure.models.base import Base

logger = logging.getLogger(__name__)


def init_database(retries: int = 15, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(engine)
            return
        except DBAPIError:
            if attempt == retries:
                raise
            logger.warning("Baza niedostępna (próba %s/%s), ponawiam", attempt, retries)
            time.sleep(delay)