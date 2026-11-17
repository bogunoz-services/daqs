from dataclasses import dataclass

from experiment.application.experiment_service import ExperimentService


@dataclass(frozen=True)
class Services:
    experiment: ExperimentService
