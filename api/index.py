from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HEDRA_API_KEY = os.getenv("HEDRA_API_KEY", "")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "AI Talking Animal Comedy Studio API",
        "endpoints": ["/api/generate"]
    })

@app.route("/api/generate", methods=["POST"])
def generate_comedy():
    data = request.json or {}
    char1 = data.get("char1", "Monkey")
    char2 = data.get("char2", "Goat")
    language = data.get("language", "English")
    topic = data.get("topic", "Late Alarm Clock")
    
    # Return mock structured response for serverless test
    return jsonify({
        "success": True,
        "message": f"Generated {language} comedy script between {char1} and {char2}!",
        "script": [
            {"character": char1, "text": f"Why are you always late, {char2}?"},
            {"character": char2, "text": "Because my alarm clock eats grass!"}
        ]
    })

# Vercel requires the app variable to be exposed
if __name__ == "__main__":
    app.run(debug=True)
