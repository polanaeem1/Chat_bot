import requests
import time
import subprocess
import sys
import threading

def run_server():
    # Start the Flask app in a separate process
    subprocess.run([sys.executable, "flask_app.py"], check=True)

def verify():
    print("Starting Flask Verification...")
    
    # Needs a moment for server to start if running via subprocess, 
    # but for simplicity we assume the user will run this while server is active
    # OR we just try to hit it. 
    # Actually, let's just assume the user runs the server in another terminal,
    # OR we try to start it. Starting it is safer.
    
    server_process = subprocess.Popen([sys.executable, "flask_app.py"])
    time.sleep(3) # Wait for startup
    
    try:
        url = "http://127.0.0.1:5000/chat"
        
        # Test 1: Simple Greeting
        payload = {
            "user_id": "TestUser_1",
            "message": "Hi, do you have parking?"
        }
        print(f"\nSending Request 1: {payload}")
        try:
            resp = requests.post(url, json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
        except Exception as e:
            print(f"Request failed: {e}")

        # Test 2: Different User
        payload2 = {
            "user_id": "TestUser_2",
            "message": "Is Main Street free?"
        }
        print(f"\nSending Request 2: {payload2}")
        try:
            resp = requests.post(url, json=payload2)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
        except Exception as e:
            print(f"Request failed: {e}")

    finally:
        print("\nStopping server...")
        server_process.terminate()

if __name__ == "__main__":
    verify()
