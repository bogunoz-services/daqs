from experiment.config.config import save_channel_map, save_connection_config


class JsonConfigStore:
    def save_channel_map(self, channels: dict) -> None:
        save_channel_map(channels)

    def save_connection_config(self, connection: dict) -> None:
        save_connection_config(connection)