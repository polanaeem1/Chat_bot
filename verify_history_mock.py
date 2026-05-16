import test
import unittest.mock
from unittest.mock import MagicMock


def verify_history_logic():
    print("Starting Mock History Verification...")
    
    # Mock the client and genai
    mock_client = MagicMock()
    test.client = mock_client
    test.current_user_id = "HistoryTester"
    
    # We need to mock the response of the model
    # First turn: User says "My name is Alice"
    # We don't care about the response content heavily, just that the call happens.
    # But to continue the test, we simulated a response.
    
    mock_response = MagicMock()
    mock_response.text = '{"response": "Hello Alice."}'
    mock_client.models.generate_content.return_value = mock_response
    
    history = []
    print("\nTURN 1: User input 'My name is Alice'")
    resp1 = test.chat_with_agent("My name is Alice", history)
    history.append("User: My name is Alice")
    history.append(f"Model: {resp1}")
    
    # Turn 2: User asks "What is my name?"
    # Now we inspect the CALL arguments of the SECOND call to see if history was passed.
    print("TURN 2: User input 'What is my name?'")
    resp2 = test.chat_with_agent("What is my name?", history)
    
    # Check the latest call args
    call_args = mock_client.models.generate_content.call_args
    # call_args.kwargs['contents'] should be the list
    
    if not call_args:
        print("FAIL: generate_content was not called.")
        return

    contents = call_args.kwargs.get('contents') or call_args.args[1] # approximating
    
    print("\nInspecting contents sent to Gemini:")
    found_alice = False
    for item in contents:
        print(f" - {item}")
        if "My name is Alice" in str(item):
            found_alice = True
            
    if found_alice:
        print("\nPASS: The previous user message 'My name is Alice' was found in the prompt contents.")
    else:
        print("\nFAIL: History was NOT found in the prompt contents.")

if __name__ == "__main__":
    verify_history_logic()
