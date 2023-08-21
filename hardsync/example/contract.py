class MeasureVoltage:
    class Request:
        integration_time: int
        channel: int

    class Response:
        voltage: float
