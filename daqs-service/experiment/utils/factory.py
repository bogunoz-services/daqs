from pathlib import Path
import pyvisa

from daq6510.instrument import DAQ6510
from daq6510.transport.visa_connection import VisaConnection
from experiment.config.config import load_channel_map, load_connection_config, KALMAN_PROCESS_VARIANCE, \
    KALMAN_MEASUREMENT_VARIANCE
from experiment.core.orchestrator import Orchestrator
from experiment.core.ports import MeasurementSink


def build_orchestrator(sink: MeasurementSink) -> Orchestrator:
    connection_config = load_connection_config()
    channel_map = load_channel_map()

    if connection_config["use_simulator"]:
        sim_file = Path(__file__).parent.parent / "daq6510" / "sim" / "daq6510_sim.yaml"
        resource_manager = pyvisa.ResourceManager(f"{sim_file}@sim")
        resource_address = "USB::0x05E6::0x6510::12345678::INSTR"
        device_hash = connection_config["device_hash"]

    else:
        resource_manager = pyvisa.ResourceManager("@py")
        resource_address = connection_config["resource_address"]
        device_hash = connection_config["device_hash"]

    connection = VisaConnection(resource_address, resource_manager)
    try:
        connection.open()
    except Exception as e:
        print(e)

    daq = DAQ6510(connection)
    return Orchestrator(daq, channel_map, device_hash,
                        KALMAN_PROCESS_VARIANCE, KALMAN_MEASUREMENT_VARIANCE, sink)
