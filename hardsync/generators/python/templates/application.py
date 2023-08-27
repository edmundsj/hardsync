from generated.client import Client
client = Client()

response = client.request_ping()
print(response)