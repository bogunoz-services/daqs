from daq6510.scpi.exceptions import IdnFormatResponseError, ChannelReadingsError, TemperatureParseError


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

def parse_temperature_line(raw: str) -> dict[str, float]:
    """
    Oczekiwany format (dostosować do realnego urządzenia), np.:
      "23.51 24.03"
      "23.51,24.03"
      "T_hot=23.51 T_cold=24.03"
    """
    raw = raw.strip()
    if not raw:
        raise TemperatureParseError("empty line")

    # wariant prosty: dwa floaty rozdzielone spacją lub przecinkiem
    for sep in (",", ";", "\t", " "):
        if sep in raw:
            parts = [p for p in raw.replace(";", ",").replace("\t", " ").split() if p]
            # jeśli było "a,b" bez spacji
            if len(parts) == 1 and "," in parts[0]:
                parts = parts[0].split(",")
            if len(parts) >= 2:
                try:
                    t1 = float(parts[0].replace(",", "."))
                    t2 = float(parts[1].replace(",", "."))
                    return {"t_hot": t1, "t_cold": t2}
                except ValueError as e:
                    raise TemperatureParseError(raw) from e

    raise TemperatureParseError(f"unrecognized format: {raw!r}")