import requests


BASE_URL = "https://donald-deadliest-jayla.ngrok-free.dev/api"

print("\n" + "="*60)
print("Testing Garage 1 (Fayoum University)")
print("="*60)

response = requests.get(f"{BASE_URL}/garages/slots-status/1", timeout=10)
print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse:")
import json
print(json.dumps(response.json(), indent=2))
