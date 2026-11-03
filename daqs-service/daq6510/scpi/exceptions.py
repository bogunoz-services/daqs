class CommandError(Exception):
    """Bazowy wyjątek dla wszystkich błędów obsługi komend."""
    pass

class IdnFormatResponseError(CommandError):
    pass

class ChannelReadingsError(CommandError):
    pass

class TcTypeValueError(CommandError):
    pass