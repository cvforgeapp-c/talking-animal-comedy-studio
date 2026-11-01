from flask import Flask, jsonify, request
import os
import uuid
import psycopg2

app = Flask(__name__)

# Load environment variables securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HEDRA_API_KEY = os.getenv("HEDRA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_db_connection():
    """Helper to connect to Neon PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)

@app.route("/", methods=["GET"])
def home():
    # Serves the complete frontend UI directly from Flask to prevent any Vercel 404 errors
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Talking Animal Comedy Studio</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white min-h-screen flex flex-col items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-800 p-6 rounded-2xl shadow-xl border border-slate-700">
            <h1 class="text-2xl font-bold mb-2 text-center text-yellow-400">animale.ai</h1>
            <p class="text-slate-400 text-sm text-center mb-6">AI Talking Animal Comedy Studio</p>

            <!-- Generation Form -->
            <div id="form-container" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Character 1</label>
                    <input type="text" id="char1" value="Monkey" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-yellow-400">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Character 2</label>
                    <input type="text" id="char2" value="Goat" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-yellow-400">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Language</label>
                    <input type="text" id="language" value="English" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-yellow-400">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Comedy Topic</label>
                    <input type="text" id="topic" value="Late Alarm Clock" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-yellow-400">
                </div>
                <button onclick="startGeneration()" class="w-full bg-yellow-500 hover:bg-yellow-400 text-slate-950 font-bold py-3 rounded-lg transition-all shadow-lg">
                    Generate Comedy Video 🎬
                </button>
            </div>

            <!-- Status & Result Container -->
            <div id="status-container" class="hidden mt-6 text-center space-y-4">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-yellow-400 border-t-transparent"></div>
                <p id="status-text" class="text-yellow-400 font-medium">Initializing job...</p>
                <div id="script-preview" class="text-left text-xs bg-slate-900 p-3 rounded border border-slate-700 space-y-2"></div>
            </div>

            <div id="video-container" class="hidden mt-6 space-y-4">
                <h3 class="text-green-400 font-bold">Video Ready! 🎉</h3>
                <video id="result-video" controls class="w-full rounded-lg border border-slate-700"></video>
                <button onclick="resetForm()" class="w-full bg-slate-700 hover:bg-slate-600 py-2 rounded-lg text-sm">Create Another</button>
            </div>
        </div>

        <script>
            let pollInterval = null;

            async function startGeneration() {
                const char1 = document.getElementById('char1').value;
                const char2 = document.getElementById('char2').value;
                const language = document.getElementById('language').value;
                const topic = document.getElementById('topic').value;

                document.getElementById('form-container').classList.add('hidden');
                document.getElementById('status-container').classList.remove('hidden');
                document.getElementById('status-text').innerText = "Registering job & generating script...";

                try {
                    const response = $_$fetch('/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ char1, char2, language, topic })
                    });
                    const data = await response.json();

                    if (data.success) {
                        if (data.script) {
                            let html = `<p class="text-slate-400 font-bold">Script Preview:</p>`;
                            data.script.forEach(line => {
                                html += `<p><strong class="text-yellow-400">${line.character}:</strong> ${line.text}</p>`;
                            });
                            document.getElementById('script-preview').innerHTML = html;
                        }

                        document.getElementById('status-text').innerText = "Job queued! Processing audio and video...";
                        pollInterval = setInterval(() => checkJobStatus(data.job_id), 3000);
                    } else {
                        alert("Error: " + data.error);
                        resetForm();
                    }
                } catch (err) {
                    alert("Network error: " + err.message);
                    resetForm();
                }
            }

            async function checkJobStatus(jobId) {
                try {
                    const res = await fetch(`/api/job-status?job_id=${jobId}`);
                    const data = await res.json();

                    if (data.success) {
                        if (data.status === 'completed') {
                            clearInterval(pollInterval);
                            document.getElementById('status-container').classList.add('hidden');
                            document.getElementById('video-container').classList.remove('hidden');
                            if (data.video_url) {
                                document.getElementById('result-video').src = data.video_url;
                            }
                        } else if (data.status === 'failed') {
                            clearInterval(pollInterval);
                            alert("Video generation failed on server.");
                            resetForm();
                        }
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }

            function resetForm() {
                clearInterval(pollInterval);
                document.getElementById('video-container').classList.add('hidden');
                document.getElementById('status-container').classList.add('hidden');
                document.getElementById('form-container').classList.remove('hidden');
            }
        </script>
    </body>
    </html>
    """.replace('$_$','await ')

@app.route("/api/generate", methods=["POST"])
def generate_comedy():
    data = request.json or {}
    char1 = data.get("char1", "Monkey")
    char2 = data.get("char2", "Goat")
    language = data.get("language", "English")
    topic = data.get("topic", "Late Alarm Clock")
    
    job_id = str(uuid.uuid4())
    
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
        print(f"Database warning: {str(e)}")

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

if __name__ == "__main__":
    app.run(debug=True)
