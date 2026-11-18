import logging
import time

from sqlalchemy.exc import DBAPIError

from infrastructure.database.connection import engine
from infrastructure.database.dev_seed import seed_dev_data
from infrastructure.models.base import Base

logger = logging.getLogger(__name__)


import logging
import time

from sqlalchemy.exc import DBAPIError

from infrastructure.database.connection import engine
from infrastructure.database.dev_seed import seed_dev_data
from infrastructure.models.base import Base

logger = logging.getLogger(__name__)


def init_database(retries: int = 15, delay: float = 2.0) -> None:
    print("1. INIT DATABASE", flush=True)

    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(engine)
            print("2. TABLES CREATED", flush=True)
            break
        except DBAPIError:
            if attempt == retries:
                raise
            time.sleep(delay)

    print("3. BEFORE SEED", flush=True)
    seed_dev_data()
    print("4. AFTER SEED", flush=True)
