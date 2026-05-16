import requests
import difflib


BASE_URL = "https://donald-deadliest-jayla.ngrok-free.dev/api"

# Fetch garages
response = requests.get(f"{BASE_URL}/garages/locations", timeout=10)
garages = response.json()

print("="*60)
print("GARAGE NAME MATCHING TEST")
print("="*60)

print("\nGarages from API:")
for g in garages:
    print(f"  - '{g['garageName']}'")

print("\n" + "="*60)
print("Testing fuzzy matching:")
print("="*60)

test_names = [
    "Fayoum University Garage",
    "fayoum university garage",
    "Fayoum University",
    "fayoum",
    "City Plaza",
    "AL Nassr"
]

garage_names = {g['garageName'].lower(): g for g in garages}
available_names = list(garage_names.keys())

print(f"\nAvailable names (lowercase): {available_names}")

for test_name in test_names:
    print(f"\nTest: '{test_name}'")
    
    # Exact substring match
    test_lower = test_name.lower()
    exact_match = None
    for garage in garages:
        if test_lower in garage['garageName'].lower():
            exact_match = garage['garageName']
            break
    
    if exact_match:
        print(f"  ✓ Exact substring match: '{exact_match}'")
    else:
        print(f"  ✗ No exact substring match")
    
    # Fuzzy match
    close_matches = difflib.get_close_matches(test_lower, available_names, n=1, cutoff=0.6)
    if close_matches:
        matched_garage = garage_names[close_matches[0]]
        print(f"  ✓ Fuzzy match: '{matched_garage['garageName']}'")
    else:
        print(f"  ✗ No fuzzy match")
