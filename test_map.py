import requests

def reverse_geocode(lat, lng):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json"
    }
    headers = {
        "User-Agent": "garage-booking-bot"
    }

    r = requests.get(url, params=params, headers=headers)
    data = r.json()

    return data["display_name"]

print(reverse_geocode(30.0444, 31.2357))