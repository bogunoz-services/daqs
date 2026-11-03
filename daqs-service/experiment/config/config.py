
import json
from pathlib import Path
from dataclasses import dataclass
import sys
from pathlib import Path

def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS, *parts)
    return Path(__file__).resolve().parents[2].joinpath(*parts)

CONFIG_PATH = resource_path("experiment", "config", "channel_config.json")
CONNECTION_CONFIG_PATH = resource_path("experiment", "config", "connection_config.json")

@dataclass(frozen=True)
class ChannelRole:
    name: str
    address: str  # zbudowany z slot+channel, np. "101"

def load_channel_map() -> dict[str, ChannelRole]:
    with open(CONFIG_PATH) as f:
        raw = json.load(f)

    return {
        name: ChannelRole(
            name=name,
            address=f"{int(data['slot'])}{int(data['channel']):02d}"
        )
        for name, data in raw.items()
    }

def save_channel_map(raw_config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        try:
            json.dump(raw_config, f, indent=2)
        except Exception as e:
            print(e)

def load_connection_config() -> dict:
    with open(CONNECTION_CONFIG_PATH) as f:
        return json.load(f)

def save_connection_config(config: dict) -> None:
    CONNECTION_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONNECTION_CONFIG_PATH, "w") as f:
        try:
            json.dump(config, f, indent=2)
        except Exception as e:
            print(e)

KALMAN_PROCESS_VARIANCE = 1e-5   # TODO: skalibruj na realnych/symulowanych danych
KALMAN_MEASUREMENT_VARIANCE = 1e-2  # TODO: skalibruj na realnych/symulowanych danych