import os
from pathlib import Path
import pyvisa

from daq6510.composite_source import CompositeMeasurementSource
from daq6510.instruments.daq6510 import DAQ6510
from daq6510.instruments.usb_temperature_reader import UsbTemperatureReader
from daq6510.transport.visa_connection import VisaConnection
from daq6510.transport.serial_connection import SerialConnection
from experiment.config.config import (
    load_channel_map,
    load_connection_config,
    KALMAN_PROCESS_VARIANCE,
    KALMAN_MEASUREMENT_VARIANCE,
)
from experiment.application.orchestrator import Orchestrator
from experiment.domain.models import MeasurementSink
from experiment.infrastructure.persistence.http_measurement_sink import HttpMeasurementSink


def build_orchestrator(sink: MeasurementSink) -> Orchestrator:
    connection_config = load_connection_config()
    channel_map = load_channel_map()
    device_hash = connection_config["device_hash"]

    # --- DAQ (VISA) ---
    if connection_config["use_simulator"]:
        sim_file = Path(__file__).parent.parent / "daq6510" / "sim" / "daq6510_sim.yaml"
        resource_manager = pyvisa.ResourceManager(f"{sim_file}@sim")
        resource_address = "USB::0x05E6::0x6510::12345678::INSTR"
    else:
        resource_manager = pyvisa.ResourceManager("@py")
        resource_address = connection_config["resource_address"]

    visa_connection = VisaConnection(resource_address, resource_manager)
    daq = DAQ6510(visa_connection)

    # --- USB temperatury (serial) ---
    usb_cfg = connection_config["temperature_usb"]
    serial_connection = SerialConnection(
        port=usb_cfg["port"],
        baudrate=usb_cfg.get("baudrate", 9600),
        timeout=usb_cfg.get("timeout", 1.0),
    )
    temp_reader = UsbTemperatureReader(serial_connection)

    voltage_channel = channel_map["voltage_probe"].address

    source = CompositeMeasurementSource(
        voltage_instrument=daq,
        temperature_instrument=temp_reader,
        voltage_channel=voltage_channel,
    )
    source.connect()

    sink = HttpMeasurementSink(
        base_url=os.environ["MEASUREMENT_SERVICE_URL"]
    )

    return Orchestrator(
        source=source,
        device_hash=device_hash,
        process_variance=KALMAN_PROCESS_VARIANCE,
        measurement_variance=KALMAN_MEASUREMENT_VARIANCE,
        measurement_sink=sink,
    )