from enum import Enum


class ExperimentActions(Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
    DEVICE_STATUS = "device_status"
    GET_HISTORY = "get_history"
    UPDATE_CHANNEL_MAP = "update_channel_map"
    UPDATE_CONNECTION_CONFIG = "update_connection_config"

