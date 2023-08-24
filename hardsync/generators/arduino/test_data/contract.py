class MeasureVoltage:
    class Request:
        channel: int
        integration_time: float

    class Response:
        voltage: float

