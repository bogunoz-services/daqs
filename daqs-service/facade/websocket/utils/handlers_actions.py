from enum import Enum


class ExperimentActions(Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
    DEVICE_STATUS = "device_status"
    GET_HISTORY = "get_history"
    UPDATE_CHANNEL_MAP = "update_channel_map"
    UPDATE_CONNECTION_CONFIG = "update_connection_config"

class DatabaseActions(Enum):
    GET_DEVICE = "get_device"
    GET_ALL_DEVICES = "get_all_devices"
    ADD_NEW_DEVICE = "add_new_device"
    UPDATE_DEVICE = "update_device"
    DELETE_DEVICE = "delete_device"
    LIST_MEASUREMENTS = "list_measurements"

