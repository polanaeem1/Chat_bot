from flask import Flask, request, jsonify
import logging
import test  # This imports your existing chatbot logic


# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Smart Parking Chatbot</h1><p>Server is running. Send POST requests to /chat.</p>"

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return jsonify({"status": "Server is running", "message": "Send a POST request with 'user_id', 'message', 'latitude', and 'longitude' to chat."})

    """
    Endpoint to handle chat messages.
    Expected JSON payload:
    {
        "user_id": "string",
        "message": "string",
        "latitude": float,
        "longitude": float,
        "history": ["optional list of strings"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        user_id = data.get('user_id')
        message = data.get('message')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        history = data.get('history', [])

        if not user_id or not message:
            return jsonify({"error": "Missing 'user_id' or 'message'"}), 400
        
        if latitude is None or longitude is None:
            return jsonify({"error": "Missing 'latitude' or 'longitude'"}), 400

        # Call the chatbot agent with location
        logging.info(f"Received message from {user_id} at ({latitude}, {longitude}): {message}")
        response = test.chat_with_agent(message, history, user_id, latitude, longitude)
        
        return jsonify({
            "response": response,
            "user_id": user_id
        })

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # This is for local testing only. 
    # PythonAnywhere uses the 'app' object directly via WSGI.
    app.run(debug=True, port=5000)
