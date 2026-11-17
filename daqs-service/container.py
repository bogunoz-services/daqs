from dataclasses import dataclass

from experiment.service.experiment_service import ExperimentService


@dataclass(frozen=True)
class Services:
    experiment: ExperimentService
