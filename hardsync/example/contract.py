class MeasureVoltage:
    class Request:
        integration_time: float
        channel: int

    class Response:
        voltage: float
