import json
from datetime import datetime, timedelta
import requests

# تاريخ في المستقبل
future_start = (datetime.utcnow() + timedelta(hours=2)).isoformat()
future_end = (datetime.utcnow() + timedelta(hours=3)).isoformat()

payload = {
  "bookingStart": "2026-01-30T12:39:19.923Z",
  "bookingEnd": "2026-01-31T12:39:19.923Z",
  "applicationUserId": "5450a353-60ad-4327-a682-6eb31eb5f62d",
  "garageId": 2,
  "priorityApplied": True,
  "price": 10.00,
  "slotNumber": "1"
}

headers = {
    "Content-Type": "application/json"
}
response = requests.get(
    "http://smartparkingsystemapp.runasp.net/api/garages/locations"
)

if response.status_code in (200, 201):
    print("[OK] Booking created successfully")
    print(json.dumps(response.json(), indent=2))
else:
    print("[FAIL] Failed to create booking")
    print(response.status_code)
    print(response.text)


# response = requests.post(
#     "https://donald-deadliest-jayla.ngrok-free.dev/api/Bookings",
#     json=payload,
#     headers=headers
# )

# if response.status_code in (200, 201):
#     print("[OK] Booking created successfully")
#     print(response.json())
# else:
#     print("[FAIL] Failed to create booking")
#     print(response.status_code)
#     print(response.text)
