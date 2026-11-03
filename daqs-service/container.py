from dataclasses import dataclass

from database.service.database_service import DatabaseService
from experiment.service.experiment_service import ExperimentService


@dataclass(frozen=True)
class Services:
    experiment: ExperimentService
    database: DatabaseService