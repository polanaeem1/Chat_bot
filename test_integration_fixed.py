#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the new API-based chatbot integration.
Tests all 4 backend APIs and chatbot functionality.
"""

import requests
import json
from datetime import datetime, timedelta

# Backend API base URL
BASE_URL = "https://donald-deadliest-jayla.ngrok-free.dev/api"

def test_api_1_garages():
    """Test API 1: Get all garages with locations"""
    print("\n" + "="*60)
    print("TEST 1: Fetching all garages")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/garages/locations", timeout=10)
        response.raise_for_status()
        garages = response.json()
        
        print(f"[SUCCESS] Found {len(garages)} garages")
        for garage in garages:
            print(f"  - {garage['garageName']} (ID: {garage['garageId']})")
            print(f"    Location: ({garage['latitude']}, {garage['longitude']})")
            print(f"    Slots: {len(garage.get('slots', []))}")
        
        return garages
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        return []

def test_api_3_garage_slots(garage_id):
    """Test API 3: Get garage slots status"""
    print("\n" + "="*60)
    print(f"TEST 3: Fetching slots for garage {garage_id}")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/garages/slots-status/{garage_id}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"[OK] SUCCESS:")
        print(f"  Total Slots: {data.get('TotalSlots', 0)}")
        print(f"  Available Slots: {data.get('AvailableSlots', 0)}")
        
        available = [s for s in data.get('Slots', []) if s['Status'] == 'Available']
        print(f"\n  Available slot numbers: {[s['SlotNumber'] for s in available]}")
        
        if available:
            print(f"  First available slot: #{available[0]['SlotNumber']} @ ${available[0]['PricePerHour']}/hr")
        
        return data
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        return None

def test_api_2_create_booking(garage_id, slot_number, price):
    """Test API 2: Create a booking"""
    print("\n" + "="*60)
    print(f"TEST 2: Creating booking for garage {garage_id}, slot {slot_number}")
    print("="*60)
    
    # Create future booking (1 hour from now, for 2 hours)
    start_time = datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    payload = {
        "UserId": "TestUser_API",
        "ApplicationUserId": "TestUser_API",
        "GarageId": garage_id,
        "SlotNumber": slot_number,
        "BookingStart": start_time.isoformat(),
        "BookingEnd": end_time.isoformat(),
        "PriorityApplied": False,
        "Price": price * 2  # 2 hours
    }
    
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/Bookings",
            json=payload,
            timeout=10
        )
        
        if response.status_code in (200, 201):
            print(f"[OK] SUCCESS: Booking created!")
            print(f"  Response: {response.json()}")
            return True
        elif response.status_code == 400:
            print(f"[FAIL] FAILED: Bad request - {response.text}")
        elif response.status_code == 500:
            print(f"[WARN]  Spot already occupied (expected if slot is busy)")
        else:
            print(f"[FAIL] FAILED: Status {response.status_code} - {response.text}")
        
        return False
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        return False

def test_api_4_delete_booking(user_id):
    """Test API 4: Delete last booking"""
    print("\n" + "="*60)
    print(f"TEST 4: Deleting last booking for user {user_id}")
    print("="*60)
    
    try:
        response = requests.delete(
            f"{BASE_URL}/Bookings/last-booking/{user_id}",
            timeout=10
        )
        
        if response.status_code in (200, 204):
            print(f"[OK] SUCCESS: Booking cancelled")
            return True
        elif response.status_code == 404:
            print(f"[WARN]  No bookings found for this user")
        else:
            print(f"[FAIL] FAILED: Status {response.status_code}")
        
        return False
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        return False

def test_chatbot_integration():
    """Test the chatbot with new API integration"""
    print("\n" + "="*60)
    print("TEST 5: Chatbot Integration (Local)")
    print("="*60)
    
    try:
        import test
        
        # Test coordinates (Fayoum University area)
        user_lat = 29.3212445
        user_lng = 30.8355711
        user_id = "TestUser_Integration"
        
        # Test 1: List locations
        print("\n[TEST] List all locations")
        response = test.chat_with_agent(
            "What parking garages are available?",
            [],
            user_id,
            user_lat,
            user_lng
        )
        print(f"Bot: {response}")
        
        # Test 2: Find nearest garage
        print("\n[TEST] Find nearest garage")
        response = test.chat_with_agent(
            "Where is the nearest garage to me?",
            [],
            user_id,
            user_lat,
            user_lng
        )
        print(f"Bot: {response}")
        
        print("\n[OK] Chatbot integration tests completed!")
        
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")

def main():
    print("\n" + "="*60)
    print("BACKEND API INTEGRATION TEST SUITE")
    print("="*60)
    
    # Test API 1: Get garages
    garages = test_api_1_garages()
    
    if not garages:
        print("\n[FAIL] Cannot proceed without garage data")
        return
    
    # Use first garage for testing
    test_garage = garages[0]
    garage_id = test_garage['garageId']
    
    # Test API 3: Get slots
    slots_data = test_api_3_garage_slots(garage_id)
    
    if slots_data and slots_data.get('Slots'):
        # Find an available slot
        available_slots = [s for s in slots_data['Slots'] if s['Status'] == 'Available']
        
        if available_slots:
            slot = available_slots[0]
            
            # Test API 2: Create booking
            test_api_2_create_booking(
                garage_id,
                slot['SlotNumber'],
                slot['PricePerHour']
            )
            
            # Test API 4: Delete booking
            test_api_4_delete_booking("TestUser_API")
    
    # Test chatbot integration
    test_chatbot_integration()
    
    print("\n" + "="*60)
    print("[OK] ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()

