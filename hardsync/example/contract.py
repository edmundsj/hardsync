class MeasureVoltage:
    class Request:
        integration_time: float
        channel: int

    class Response:
        voltage: float


# TODO: Add example for how to add a device-initiated exchange
