import logging

from database.service.database_service import DatabaseService
from experiment.core.ports import MeasurementRecord

logger = logging.getLogger(__name__)


class DatabaseMeasurementSink:
    def __init__(self, database_service: DatabaseService) -> None:
        self._database = database_service

    def write(self, record: MeasurementRecord) -> None:
        try:
            self._database.record_measurement(
                record.device_hash, record.time, record.t1, record.t2, record.voltage,
            )
        except Exception:
            logger.exception("Cannot write to database")