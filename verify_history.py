import Chatbot.test
import io
import sys


def verify_history():
    print("Starting History Verification...")
    
    test.current_user_id = "HistoryTester"
    history = []
    
    # Turn 1: State name
    print("\nTURN 1: My name is Alice.")
    # Note: We pass empty history list [] because the history is now managed INTERNALLY by test.py
    resp1 = test.chat_with_agent("My name is Alice.", [], test.current_user_id)
    print(f"Bot: {resp1}")
    
    # Turn 2: Ask for name
    print("\nTURN 2: What is my name?")
    resp2 = test.chat_with_agent("What is my name?", [], test.current_user_id)
    print(f"Bot: {resp2}")
    
    if "Alice" in resp2:
        print("\nPASS: The bot remembered the name 'Alice' from internal storage.")
    else:
        print("\nFAIL: The bot did not mention 'Alice'.")

if __name__ == "__main__":
    verify_history()
