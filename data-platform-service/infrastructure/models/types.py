from datetime import datetime, timezone

from sqlalchemy import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)      # zakładamy UTC
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime, dialect):
        return None if value is None else value.replace(tzinfo=timezone.utc)