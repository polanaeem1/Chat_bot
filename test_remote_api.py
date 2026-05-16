import requests
import sys

def test_remote():
    print("--- Remote API Tester ---")
    username = input("Enter your PythonAnywhere username: ").strip()
    if not username:
        print("Username is required.")
        return

    url = f"http://{username}.pythonanywhere.com/chat"
    print(f"\nTarget URL: {url}")
    
    # 1. Test Connectivity (GET)
    print("\n1. Testing Server Connectivity...")
    try:
        resp = requests.get(url)
        print(f"Server Status: {resp.status_code}")
        print(f"Message: {resp.json().get('message', 'No message')}")
    except Exception as e:
        print(f"Connectivity check failed: {e}")
        print("Check if you reloaded the web app in PythonAnywhere!")
        return

    # 2. Test Chat (POST)
    print("\n2. Testing Chat Functionality...")
    user_input = input("Enter a message for the bot (e.g. 'Hi'): ") or "Hi"
    
    payload = {
        "user_id": "ABC123",
        "message": user_input,
        "latitude": 30.924526,
        "longitude": 30.205753
    }
    
    try:
        resp = requests.post(url, json=payload)
        data = resp.json()
        
        if resp.status_code == 200:
            print("\nSUCCESS!")
            print(f"Bot Response: {data.get('response')}")
            print(f"User ID used: {data.get('user_id')}")
            print(f"latitude used: {data.get('latitude')}")
            print(f"longitude used: {data.get('longitude')}")
        else:
            print(f"\nFAILED (Status {resp.status_code}):")
            print(data)
            
    except Exception as e:
        print(f"Error sending POST request: {e}")

if __name__ == "__main__":
    test_remote()
