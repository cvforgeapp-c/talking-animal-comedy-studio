from flask import Flask, jsonify, request
import os
import uuid
import psycopg2

app = Flask(__name__)

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("sk_25b4c225c9483dcf9830addf98704b082080bbda20df1c60", "")
HEDRA_API_KEY = os.getenv("HEDRA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_db_connection():
    """Helper to connect to Neon PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "AI Talking Animal Comedy Studio API",
        "endpoints": ["/api/generate", "/api/job-status"],
        "version": "1.0.0"
    })

@app.route("/api/generate", methods=["POST"])
def generate_comedy():
    data = request.json or {}
    char1 = data.get("char1", "Monkey")
    char2 = data.get("char2", "Goat")
    language = data.get("language", "English")
    topic = data.get("topic", "Late Alarm Clock")
    
    # Generate a unique Job ID for asynchronous processing
    job_id = str(uuid.uuid4())
    
    # Try saving the job as 'pending' in Neon DB to prevent Vercel 10s timeouts
    try:
        if DATABASE_URL:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO video_jobs (job_id, status, char1, char2, language) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (job_id, "pending", char1, char2, language)
            )
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        # Fallback gracefully if database table hasn't been created yet during early testing
        print(f"Database warning: {str(e)}")

    # Returns instantly with job_id so Vercel never times out
    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "pending",
        "message": f"Generated {language} comedy job registration between {char1} and {char2}!",
        "script": [
            {"character": char1, "text": f"Why are you always late, {char2}?"},
            {"character": char2, "text": "Because my alarm clock eats grass!"}
        ]
    })

@app.route("/api/job-status", methods=["GET"])
def job_status():
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"success": False, "error": "Missing job_id parameter"}), 400
        
    try:
        if not DATABASE_URL:
            return jsonify({"success": True, "job_id": job_id, "status": "completed", "note": "Database URL not configured yet."})
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, video_url FROM video_jobs WHERE job_id = %s", (job_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            return jsonify({"success": False, "error": "Job not found"}), 404
            
        return jsonify({
            "success": True,
            "job_id": job_id,
            "status": row[0],
            "video_url": row[1] if row[1] else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Vercel requires the app variable to be exposed
if __name__ == "__main__":
    app.run(debug=True)
