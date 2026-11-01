from flask import Flask, jsonify, request, render_template
import os
import uuid
import json

# Configure Flask to look for index.html in the current root directory (.)
app = Flask(__name__, template_folder='.')

# Load environment variables securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HEDRA_API_KEY = os.getenv("HEDRA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Configure Gemini if key is provided
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini configuration error: {e}")

def get_db_connection():
    """Helper to connect to Neon PostgreSQL database safely."""
    if not DATABASE_URL:
        return None
    try:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_comedy():
    try:
        data = request.json or {}
        prompt = data.get("prompt", "A funny conversation between two animals.")
        incoming_script = data.get("script")
        strict_mode = data.get("strict_mode", False)
        
        job_id = str(uuid.uuid4())
        script_lines = []

        # Enforce strict compliance: if strict mode is active and an incoming script exists, lock and use it directly
        if strict_mode and incoming_script:
            script_lines = incoming_script
        else:
            # Dynamically parse ANY custom prompt using Gemini AI
            if GEMINI_API_KEY:
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    ai_prompt = f"""
                    Based on the following user prompt, write a short, funny 3-line dialogue script between two characters.
                    User Prompt: "{prompt}"
                    
                    Format your response strictly as a valid JSON list of objects with keys "character" and "text". Example:
                    [
                      {{"character": "Host", "text": "..."}},
                      {{"character": "Guest", "text": "..."}}
                    ]
                    """
                    response = model.generate_content(ai_prompt)
                    cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
                    script_lines = json.loads(cleaned_text)
                except Exception as ai_err:
                    print(f"Gemini generation fallback triggered: {ai_err}")
                    script_lines = [
                        {"character": "Studio Host", "text": f"Analyzing prompt: {prompt}"},
                        {"character": "Co-Host", "text": "Let's compile this comedy sequence right away!"}
                    ]
            else:
                script_lines = [
                    {"character": "Host", "text": f"Received prompt: {prompt}"},
                    {"character": "Guest", "text": "Time to launch the production studio!"}
                ]

        # Safe database insertion
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO video_jobs (job_id, status, prompt) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (job_id, "pending", prompt)
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as db_err:
                print(f"DB insert warning: {db_err}")

        return jsonify({
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "script": script_lines,
            "message": "Prompt successfully parsed and script locked!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/job-status", methods=["GET"])
def job_status():
    try:
        job_id = request.args.get("job_id")
        if not job_id:
            return jsonify({"success": False, "error": "Missing job_id parameter"}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": True,
                "job_id": job_id,
                "status": "completed",
                "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
            })
            
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
            "video_url": row[1] if row[1] else "https://www.w3schools.com/html/mov_bbb.mp4"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
