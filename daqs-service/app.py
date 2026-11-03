import asyncio
import sys
from functools import partial
from pathlib import Path

import pyvisa

from adapters.measurement_sink import DatabaseMeasurementSink
from container import Services
from database.infrastructure.database.connection import SessionFactory
from database.infrastructure.database.dev_seed import seed_dev_data
from database.infrastructure.database.init import init_database
from database.service.database_service import DatabaseService
from experiment.config.store import JsonConfigStore
from experiment.service.experiment_service import ExperimentService
from experiment.utils.factory import build_orchestrator
from facade.api import build_websocket_api


def get_sim_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)


async def initialize_services() -> Services:
    sim_yaml = get_sim_path("daq6510/sim/daq6510_sim.yaml")
    resource_manager = pyvisa.ResourceManager(f"{sim_yaml}@sim")
    print(resource_manager.list_resources())

    await asyncio.to_thread(init_database)
    await asyncio.to_thread(seed_dev_data)

    database_service = DatabaseService(SessionFactory)
    measurement_sink = DatabaseMeasurementSink(database_service)
    config_store = JsonConfigStore()
    experiment_service = ExperimentService(
        partial(build_orchestrator, measurement_sink),
        config_store,
    )

    return Services(experiment=experiment_service, database=database_service)


async def main() -> None:
    services = await initialize_services()
    api = build_websocket_api(services, host="0.0.0.0", port=12345)

    try:
        await api.run()
    except KeyboardInterrupt:
        print("Shutting down daqs-service...")


if __name__ == "__main__":
    asyncio.run(main())