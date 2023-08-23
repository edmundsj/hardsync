from generated.client import Client

# Have the device read the voltage, and return the desired value
client = Client()
voltage = client.request_measure_voltage(channel=1, integration_time=0.5)

# Listen for communication initiated from the device
with client.listen():
    client.respond()