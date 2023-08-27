class MeasureVoltage:
    class Request:
        integration_time: float
        channel: int

    class Response:
        voltage: float


class Channel:
    class Host:
        write_bytes = "serial.write"
        read_until = "serial.read_until"
    class Device:
        write_bytes = "Serial.print"
        read_until = "Serial.read"

# TODO: Add example for how to add a device-initiated exchange
