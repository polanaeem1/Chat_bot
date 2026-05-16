#!/usr/bin/env python3
import json
import logging
import os
import difflib
import random
import uuid
import requests
import math
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# -----------------------------
# Gemini API Keys 
# Replace the keys with your own valid keys
# -----------------------------
API_KEYS = [
    "AIzaSyBsgPTxJ5pntEbfov2IkfVZ7IbMvZbiq7E",
    "AIzaSyCXnv6a9DF4dUl4xRXuhuezj1amowju2vw",
    "AIzaSyBXdIf-1yPkjuy1TbPA2psw3AryR9CqOog",
    "AIzaSyA9c__L4VqKvo_Pqzq0Lr-b9DZPuzAJlM4",
    "AIzaSyC6wAtVY_KhQdmiQQx9g08b8DAfCI50CUY"
]
key_index = 0

try:
    from google import genai
    client = genai.Client(api_key=API_KEYS[key_index])
except Exception as e:
    # If genai isn't available, we still provide a fallback that returns unknown intent.
    logging.warning("Could not import google.genai client. Gemini calls will be simulated. (%s)", e)
    genai = None
    client = None

# -----------------------------
# Backend API Configuration
# -----------------------------
BACKEND_BASE_URL = "https://donald-deadliest-jayla.ngrok-free.dev/api"

# -----------------------------
# Persistent storage setup
# -----------------------------
HISTORY_FILE = "chat_history.json"

# Load/Save Helpers for History
def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_chat_history(history_data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save history: {e}")

# -----------------------------
# API Client Functions
# -----------------------------

def fetch_all_garages():
    """Fetch all garages with their locations and slots from API 1."""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/garages/locations",
                timeout=15  # Increased timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Connection failed (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error(f"Failed to fetch garages after {max_retries} attempts: {e}")
                return []
        except requests.RequestException as e:
            logging.error(f"Failed to fetch garages: {e}")
            return []
    
    return []

def fetch_garage_slots(garage_id: int):
    """Fetch detailed slot information for a specific garage."""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/garages/slots-status/{garage_id}",
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Connection failed for garage {garage_id} (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"Failed to fetch garage slots after {max_retries} attempts: {e}")
                return None
        except requests.RequestException as e:
            logging.error(f"Failed to fetch garage slots for garage {garage_id}: {e}")
            return None
    
    return None

def create_booking_api(payload: dict):
    """Create a booking via API 2."""
    max_retries = 2  # Fewer retries for booking to avoid duplicate bookings
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/Bookings",
                json=payload,
                timeout=15
            )
            
            if response.status_code in (200, 201):
                return {
                    'success': True,
                    'message': 'Booking created successfully',
                    'data': response.json()
                }
            elif response.status_code == 400:
                return {
                    'success': False,
                    'error': 'Invalid booking request. Please check your details.'
                }
            elif response.status_code == 500:
                return {
                    'success': False,
                    'error': 'This spot is already occupied. Please choose another.'
                }
            else:
                return {
                    'success': False,
                    'error': f'Booking failed with status {response.status_code}'
                }
        
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Connection failed for booking (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"Failed to create booking after {max_retries} attempts: {e}")
                return {
                    'success': False,
                    'error': 'Unable to connect to booking system. Please try again.'
                }
        except requests.RequestException as e:
            logging.error(f"Failed to create booking: {e}")
            return {
                'success': False,
                'error': 'Unable to connect to booking system. Please try again.'
            }
    
    return {
        'success': False,
        'error': 'Booking failed after multiple attempts.'
    }

def delete_last_booking_api(user_id: str):
    """Delete the last booking for a user via backend API."""
    try:
        response = requests.delete(
            f"{BACKEND_BASE_URL}/Bookings/last-booking/{user_id}",
            timeout=10
        )
        if response.status_code in (200, 204):
            return {"success": True, "message": "Booking cancelled successfully"}
        elif response.status_code == 404:
            return {"success": False, "error": "No active bookings found"}
        else:
            return {"success": False, "error": f"Failed to cancel booking: {response.status_code}"}
    except requests.RequestException as e:
        logging.error(f"Failed to delete booking: {e}")
        return {"success": False, "error": "Unable to connect to booking system. Please try again."}

# -----------------------------
# Geolocation Helper Functions
# -----------------------------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def find_nearest_garage(user_lat: float, user_lng: float):
    """Find the nearest garage to the user's location."""
    garages = fetch_all_garages()
    if not garages:
        return None
    
    nearest = None
    min_distance = float('inf')
    
    for garage in garages:
        distance = haversine_distance(
            user_lat, user_lng,
            garage['latitude'], garage['longitude']
        )
        if distance < min_distance:
            min_distance = distance
            nearest = garage
    
    if nearest:
        nearest['distance_km'] = round(min_distance, 2)
    
    return nearest

# -----------------------------
# Agentic Setup
# -----------------------------
# Required: pip install google-generativeai

# -----------------------------
# Agentic / Function Calling Setup
# -----------------------------
try:
    from google import genai
except ImportError:
    genai = None

# We'll use the same keys
API_KEYS = [
    "AIzaSyBsgPTxJ5pntEbfov2IkfVZ7IbMvZbiq7E",
    "AIzaSyCXnv6a9DF4dUl4xRXuhuezj1amowju2vw",
    "AIzaSyBXdIf-1yPkjuy1TbPA2psw3AryR9CqOog",
    "AIzaSyA9c__L4VqKvo_Pqzq0Lr-b9DZPuzAJlM4",
    "AIzaSyC6wAtVY_KhQdmiQQx9g08b8DAfCI50CUY"
]
current_key_idx = 0
client = None

def configure_genai(idx=None):
    global current_key_idx, client
    if idx is not None:
        current_key_idx = idx % len(API_KEYS)
    
    if genai:
        try:
            client = genai.Client(api_key=API_KEYS[current_key_idx])
            logging.info(f"Configured Gemini with Key Index {current_key_idx}")
        except Exception as e:
            logging.error("Failed to init client: %s", e)
            client = None

configure_genai()

# -----------------------------
# Local parking logic (API-based)
# -----------------------------

def find_garage_by_name(garage_name: str):
    """Find a garage by name with fuzzy matching."""
    garages = fetch_all_garages()
    if not garages:
        return None
    
    # Exact match first
    garage_name_lower = garage_name.lower()
    for garage in garages:
        if garage_name_lower in garage['garageName'].lower():
            return garage
    
    # Fuzzy match
    garage_names = {g['garageName'].lower(): g for g in garages}
    close_matches = difflib.get_close_matches(garage_name_lower, garage_names.keys(), n=1, cutoff=0.6)
    
    if close_matches:
        return garage_names[close_matches[0]]
    
    return None

# -----------------------------
# TOOLS (The capabilities of the bot)
# -----------------------------

def tool_list_locations():
    """Returns a list of all garage names."""
    garages = fetch_all_garages()
    if not garages:
        return "Unable to fetch garage locations at this time."
    
    garage_names = [g['garageName'] for g in garages]
    return garage_names

def tool_find_nearest_garage(user_lat: float, user_lng: float):
    """Find and return information about the nearest garage."""
    nearest = find_nearest_garage(user_lat, user_lng)
    if not nearest:
        return "Unable to find nearby garages."
    
    # Get slot details
    slots_info = fetch_garage_slots(nearest['garageId'])
    if slots_info:
        available = slots_info.get('availableSlots', 0)
        total = slots_info.get('totalSlots', 0)
        return f"Nearest garage: {nearest['garageName']} ({nearest['distance_km']} km away). Available spots: {available}/{total}"
    else:
        return f"Nearest garage: {nearest['garageName']} ({nearest['distance_km']} km away)"

def tool_get_price_estimate(garage_name: str, duration_hours: float):
    """Get price estimate for parking at a specific garage."""
    garage = find_garage_by_name(garage_name)
    if not garage:
        return f"No garage found matching '{garage_name}'."
    
    # Get slot details to find price
    slots_info = fetch_garage_slots(garage['garageId'])
    if not slots_info or not slots_info.get('slots'):
        return f"Unable to get pricing information for {garage['garageName']}."
    
    # Get price from first available slot (assuming all slots same price)
    first_slot = slots_info['slots'][0]
    price_per_hour = first_slot.get('salaryPerHour', 0)
    total_cost = price_per_hour * float(duration_hours)
    
    return f"Estimate: ${total_cost:.2f} for {duration_hours} hours at {garage['garageName']} (${price_per_hour}/hour)."

def tool_book_spot(garage_name: str, user_id: str, start_time_iso: str, duration_hours: float, user_lat: float = None, user_lng: float = None):
    """
    Books a spot at a garage for a specific time and duration.
    """
    # Find garage
    garage = None
    if garage_name:
        garage = find_garage_by_name(garage_name)
    elif user_lat is not None and user_lng is not None:
        # If no garage name, use nearest
        garage = find_nearest_garage(user_lat, user_lng)
    
    if not garage:
        return f"No garage found matching '{garage_name}'."
    
    # Parse time
    try:
        start_dt = datetime.fromisoformat(start_time_iso)
        end_dt = start_dt + timedelta(hours=float(duration_hours))
    except ValueError:
        return "Error: Invalid date/time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."
    
    # Get available slots
    slots_info = fetch_garage_slots(garage['garageId'])
    if not slots_info:
        return f"Unable to check availability for {garage['garageName']}."
    
    available_slots = [s for s in slots_info.get('slots', []) if s['status'] == 'Available']
    
    if not available_slots:
        return f"FAILED: No spots available at {garage['garageName']}."
    
    # Pick first available slot
    selected_slot = available_slots[0]
    price_per_hour = selected_slot.get('salaryPerHour', 0)
    total_price = price_per_hour * float(duration_hours)
    
    # Create booking payload
    payload = {
        "UserId": user_id,
        "ApplicationUserId": user_id,
        "GarageId": garage['garageId'],
        "SlotNumber": selected_slot['slotnumber'],
        "BookingStart": start_dt.isoformat(),
        "BookingEnd": end_dt.isoformat(),
        "PriorityApplied": False,
        "Price": total_price
    }
    
    # Call API
    result = create_booking_api(payload)
    
    if result['success']:
        return f"SUCCESS: Booked spot #{selected_slot['SlotNumber']} at {garage['garageName']}. Cost: ${total_price:.2f}. Time: {start_dt} to {end_dt}."
    else:
        return f"FAILED: {result['error']}"

def tool_cancel_booking(user_id: str):
    """Cancels the MOST RECENT booking for this user."""
    result = delete_last_booking_api(user_id)
    
    if result['success']:
        return f"SUCCESS: {result['message']}"
    else:
        return result['error']

# -----------------------------
# Agent Logic (The "Brain")
# -----------------------------
AGENT_SYSTEM_PROMPT = """
You are an intelligent parking assistant agent.
Current Server Time: {{CURRENT_TIME}}

You have access to the following tools:
1. `list_locations()`: See all available parking garages.
2. `find_nearest_garage(user_lat, user_lng)`: Find the closest garage to the user's location.
3. `get_price_estimate(garage_name, duration_hours)`: Check cost for parking at a specific garage.
4. `book_spot(garage_name, user_id, start_time_iso, duration_hours, user_lat=None, user_lng=None)`: 
   - Book a spot at a garage.
   - You MUST convert natural language times (e.g. "tomorrow at 2pm") into ISO format (YYYY-MM-DDTHH:MM:SS) based on the Current Server Time.
   - If user doesn't specify duration, assume 1 hour.
   - If user doesn't specify garage name but provides location, use nearest garage.
5. `cancel_booking(user_id)`: Cancel the user's last booking.

**INSTRUCTIONS**:
1. Always check Current Server Time before making timestamps.
2. Output JSON decision: `{ "tool": "...", "args": {...} }` or `{ "response": "..." }`.
3. If the user asks "How much", use `get_price_estimate`.
4. If the user asks "where can I park" or "nearest garage", use `find_nearest_garage`.
5. Be helpful and polite.
6. IMPORTANT: PASS THE 'user_id' ARGUMENT when calling book/cancel tools.
7. User location (lat/lng) is available for finding nearest garages.
"""

def chat_with_agent(user_input: str, history: list, user_id: str, user_lat: float = None, user_lng: float = None, retry_count: int = 0):
    """
    Manages the conversation loop with built-in Key Rotation and Retries.
    Now includes user location (lat/lng) for geolocation-based features.
    """
    global current_key_idx, client
    
    # Stop if we've cycled through all keys
    if retry_count >= len(API_KEYS):
        return "System Error: All API keys have reached their quota limits. Please wait or upgrade your plan."

    
    # 1. Load persistent history for this user
    all_history = load_chat_history()
    user_history = all_history.get(user_id, [])
    
    # 2. Merge with any temporary history passed in (optional, usually empty now)
    # We prioritize the persistent history.
    if history:
        # If the caller passed history, maybe we should append it? 
        # For now, let's just use the persistent 'user_history' as the source of truth.
        pass

    if not client:
        return "Error: `google-genai` client not configured. Please identify python environment."

    # History is ignored in this stateless demo snippet for simplicity, 
    # but we include system prompt + user input
    
    # Construct content with system prompt first
    # Using explicit prompt construction for the 'Client' SDK
    # Inject dynamic time into system prompt
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_prompt_dynamic = AGENT_SYSTEM_PROMPT.replace("{{CURRENT_TIME}}", current_time_str)

    contents = [
        system_prompt_dynamic,
        f"Active Session ID: {user_id}"
    ]
    
    # Add conversation history
    for msg in user_history:
        contents.append(msg)
        
    # Add current user input
    contents.append(f"User Input: {user_input}")
    
    try:
        # 1. Ask Gemini what to do
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        text = getattr(response, "text", "") or str(response)
        text = text.strip()
        
        # 2. Parse JSON decision
        # Clean up markdown
        text = text.replace("```json", "").replace("```", "").strip()
        
        import json
        try:
            decision = json.loads(text)
        except json.JSONDecodeError:
            # Fallback if Gemini talks normally
            # SAVE HISTORY before returning
            user_history.append(f"User: {user_input}")
            user_history.append(f"Model: {text}")
            all_history[user_id] = user_history
            save_chat_history(all_history)
            return text

        # 3. Handle Decision
        if "tool" in decision:
            tool_name = decision["tool"]
            args = decision.get("args", {})
            
            # Execute Tool
            result = None
            if tool_name == "list_locations":
                result = tool_list_locations()
            elif tool_name == "find_nearest_garage":
                # Use provided coordinates or from args
                lat = args.get("user_lat", user_lat)
                lng = args.get("user_lng", user_lng)
                if lat is None or lng is None:
                    result = "Error: User location required for this feature."
                else:
                    result = tool_find_nearest_garage(lat, lng)
            elif tool_name == "get_price_estimate":
                result = tool_get_price_estimate(args.get("garage_name"), args.get("duration_hours", 1.0))
            elif tool_name == "book_spot":
                result = tool_book_spot(
                    args.get("garage_name"), 
                    user_id,
                    args.get("start_time_iso"),
                    args.get("duration_hours", 1.0),
                    user_lat,
                    user_lng
                )
            elif tool_name == "cancel_booking":
                result = tool_cancel_booking(user_id)
            else:
                result = "Error: Unknown tool."
            
            # 4. Feed result back to ask for final response
            # We must include history here too for context continuity if needed, 
            # though usually immediate context is enough.
            # For simplicity, we just remind the agent of the specific interaction.
            final_prompt_contents = [
                system_prompt_dynamic,
                f"Active Session ID: {user_id}"
            ]
            # (Optional) Re-add history? 
            # Ideally yes, but let's keep it simple for the tool-response turn.
            # The tool result is the most critical context now.
            
            final_prompt_contents.append(f"User asked: {user_input}")
            final_prompt_contents.append(f"You called tool: {tool_name}")
            final_prompt_contents.append(f"Result was: {result}")
            final_prompt_contents.append("Now provide a helpful response to the user.")
            
            final_resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=final_prompt_contents
            )
            final_text = getattr(final_resp, "text", "") or str(final_resp)
            
            # SAVE HISTORY
            user_history.append(f"User: {user_input}")
            user_history.append(f"Model: {final_text}")
            all_history[user_id] = user_history
            save_chat_history(all_history)
            
            return final_text
            
        elif "response" in decision:
            text_resp = decision["response"]
            # SAVE HISTORY
            user_history.append(f"User: {user_input}")
            user_history.append(f"Model: {text_resp}")
            all_history[user_id] = user_history
            save_chat_history(all_history)
            return text_resp
        else:
            final_text = str(text)
            # SAVE HISTORY
            user_history.append(f"User: {user_input}")
            user_history.append(f"Model: {final_text}")
            all_history[user_id] = user_history
            save_chat_history(all_history)
            return final_text

    except Exception as e:
        error_str = str(e).upper()
        if "429" in error_str or "EXHAUSTED" in error_str:
            logging.warning(f"Quota exceeded for Key {current_key_idx}. Rotating...")
            import time
            time.sleep(1) # Small delay before retry
            configure_genai(current_key_idx + 1)
            return chat_with_agent(user_input, history, user_id, retry_count + 1)
            
        logging.error("Gemini Error: %s", e)
        return f"System Error: {e}"

def cli():
    # Use fixed user ID for testing
    user_id = "ABC123"
    
    print("Welcome to the Smart Agent Garage System!")
    print("(Powered by Gemini Agentic Workflow)")
    print(f"Session started for: {user_id}")
    print("Commands: 'exit' only.")
    
    history = []
    
    while True:
        try:
            user_msg = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_msg.lower() in ["exit", "quit"]:
            print("Bye!")
            break
            
        if not user_msg:
            continue
            
        reply = chat_with_agent(user_msg, history, user_id)
        print(f"Bot: {reply}")
        
        # Update history
        history.append(f"User: {user_msg}")
        history.append(f"Model: {reply}")

if __name__ == "__main__":
    cli()
