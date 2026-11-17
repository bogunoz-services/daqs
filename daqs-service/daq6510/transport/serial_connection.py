import serial
from serial import SerialException


class SerialConnection:
    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
    ):
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ser: serial.Serial | None = None

    def open(self) -> None:
        self._ser = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        )

    def readline(self) -> str:
        if self._ser is None:
            raise RuntimeError("Serial port not open")
        try:
            line = self._ser.readline()
        except SerialException as e:
            raise RuntimeError(f"USB read error: {e}") from e
        return line.decode("utf-8", errors="replace").strip()

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None