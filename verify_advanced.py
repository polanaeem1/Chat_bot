import test
import os
import json
from datetime import datetime, timedelta

def run_test():
    print("--- Starting Advanced Features Verification ---")
    
    # 1. Reset Data
    if os.path.exists("bookings.json"):
        os.remove("bookings.json")
    test.bookings = []

    user_id = "AdvancedTester"

    # 2. Test Price Estimate
    print("\n[TEST 1] Price Estimate")
    est = test.tool_get_price_estimate("Main Street", 3)
    print(f"Result: {est}") # Expect ~$6.00

    # 3. Test Future Booking (Tomorrow 2pm)
    print("\n[TEST 2] Book Future Spot")
    tmr = datetime.now() + timedelta(days=1)
    # Set to 14:00:00
    tmr = tmr.replace(hour=14, minute=0, second=0, microsecond=0)
    start_iso = tmr.isoformat()
    
    res = test.tool_book_spot("Main Street", user_id, start_iso, 2.0)
    print(f"Result: {res}")
    
    if "SUCCESS" in res:
        print("PASS: Future booking created.")
    else:
        print("FAIL: Booking failed.")

    # 4. Test Overlap (Try to book same spot 3pm-5pm)
    print("\n[TEST 3] Overlap Check")
    # Previous was 2pm-4pm. 3pm overlaps.
    tmr_overlap = tmr.replace(hour=15) 
    res_overlap = test.tool_book_spot("Main Street", "OtherUser", tmr_overlap.isoformat(), 2.0)
    print(f"Result: {res_overlap}")

    # Note: We have multiple spots on Main Street (ids 101, 102, etc.)?
    # Actually, yes. So it MIGHT succeed if it picks a different spot ID.
    # To truly test overlap on the SAME spot, we'd need to fill them all.
    # But let's see if it booked a DIFFERENT spot ID.
    
    # 5. Extension
    print("\n[TEST 4] Extend Booking")
    res_ext = test.tool_extend_booking(user_id, 1.0)
    print(f"Result: {res_ext}")
    
    # 6. Cancel
    print("\n[TEST 5] Cancel Booking")
    res_cancel = test.tool_cancel_booking(user_id)
    print(f"Result: {res_cancel}")

if __name__ == "__main__":
    run_test()
