from generated.client import Client

client = Client()

# Option 1 - have the request_measure_voltage return all information from the response.
response_name, response_values = client.request_measure_voltage(channel=1, integration_time=0.5)
voltage = response_values['voltage']

# Option 2 - have the request_measure_voltage function return only the desired information
voltage = client.request_measure_voltage(channel=1, integration_time=0.5)
