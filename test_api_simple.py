#!/usr/bin/env python3
"""
Simple API connectivity test for backend integration.
"""


import requests
import sys

BASE_URL = "https://donald-deadliest-jayla.ngrok-free.dev/api"

print("\n" + "="*60)
print("BACKEND API CONNECTIVITY TEST")
print("="*60)

# Test API 1: Get garages
print("\n[TEST 1] Fetching all garages...")
try:
    response = requests.get(f"{BASE_URL}/garages/locations", timeout=10)
    response.raise_for_status()
    garages = response.json()
    print(f"[OK] Found {len(garages)} garages")
    for g in garages:
        print(f"  - {g['garageName']} (ID: {g['garageId']})")
except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

# Test API 3: Get garage slots
if garages:
    garage_id = garages[0]['garageId']
    print(f"\n[TEST 3] Fetching slots for garage {garage_id}...")
    try:
        response = requests.get(f"{BASE_URL}/garages/slots-status/{garage_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"[OK] Total: {data.get('TotalSlots', 0)}, Available: {data.get('AvailableSlots', 0)}")
    except Exception as e:
        print(f"[FAIL] {e}")

print("\n" + "="*60)
print("API TESTS COMPLETED")
print("="*60)
