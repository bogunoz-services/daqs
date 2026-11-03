from daq6510.scpi.exceptions import IdnFormatResponseError, ChannelReadingsError


def parse_idn(raw_response: str) -> dict:
    parts = raw_response.strip().split(",")

    if len(parts) != 4:
        raise IdnFormatResponseError()

    return {
        "manufacturer": parts[0].strip(),
        "model": parts[1].strip(),
        "serial_number": parts[2].strip(),
        "firmware_version": parts[3].strip(),
    }

def parse_channel_readings(raw_response: str) -> dict[str, float]:
    parts = [p.strip() for p in raw_response.strip().split(",") if p]

    if len(parts) % 2 != 0:
        raise ChannelReadingsError()

    result: dict[str, float] = {}
    for i in range(0, len(parts), 2):
        channel = parts[i]
        value = parts[i + 1]
        try:
            result[channel] = float(value)
        except ValueError as e:
            raise ChannelReadingsError(str(e)) from e

    return result