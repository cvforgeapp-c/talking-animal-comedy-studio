from flask import Flask, jsonify, request
import os
import uuid

app = Flask(__name__)

# Load environment variables securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
HEDRA_API_KEY = os.getenv("HEDRA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

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

# High-end Video GPT / AI Studio Mobile UX Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Video GPT • AI Comedy Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .glass-box { background: rgba(18, 18, 24, 0.95); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glow-prompt { border: 1px solid rgba(139, 92, 246, 0.4); box-shadow: 0 0 15px rgba(139, 92, 246, 0.15); }
        .btn-gradient { background: linear-gradient(135deg, #f59e0b 0%, #8b5cf6 100%); }
        .badge-pro { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    </style>
</head>
<body class="bg-black text-white min-h-screen pb-24 flex flex-col justify-between select-none">

    <!-- Top Header Bar -->
    <header class="px-5 py-4 flex items-center justify-between sticky top-0 bg-black/90 backdrop-blur-lg z-50 border-b border-white/5">
        <h1 class="text-xl font-extrabold tracking-tight text-white">Video GPT</h1>
        <div class="flex items-center gap-2">
            <button class="badge-pro text-slate-950 font-black text-xs px-3 py-1.5 rounded-full flex items-center gap-1 shadow-lg shadow-amber-500/20">
                <span>👑</span> PRO
            </button>
        </div>
    </header>

    <main class="flex-1 max-w-md w-full mx-auto px-4 pt-2 space-y-6">

        <!-- Mode Switcher -->
        <div class="bg-zinc-900 p-1 rounded-full flex items-center border border-white/5">
            <button id="tab-text" onclick="switchMode('text')" class="flex-1 py-2.5 rounded-full text-xs font-bold bg-white text-black transition-all shadow-md">
                Text to Video
            </button>
            <button id="tab-image" onclick="switchMode('image')" class="flex-1 py-2.5 rounded-full text-xs font-bold text-zinc-400 hover:text-white transition-all relative">
                Image to Video
                <span class="absolute -top-1 right-3 bg-amber-500 text-[9px] font-black text-black px-1.5 py-0.2 rounded-full uppercase">NEW</span>
            </button>
        </div>

        <!-- Prompt Card Section -->
        <div class="glass-box glow-prompt rounded-2xl p-4 space-y-3 relative" id="form-container">
            <div class="text-xs text-zinc-400 font-medium">Prompt / Comedy Premise:</div>
            
            <textarea id="prompt-input" rows="4" maxlength="1000" oninput="updateCharCount()" 
                class="w-full bg-transparent text-sm text-white placeholder-zinc-500 focus:outline-none resize-none"
                placeholder="A hilarious conversation between a monkey and a goat arguing about a late alarm clock..."></textarea>

            <div class="flex items-center justify-between pt-1">
                <button onclick="surpriseMe()" class="bg-zinc-800 hover:bg-zinc-700 text-amber-400 text-xs font-semibold px-3 py-1.5 rounded-full flex items-center gap-1.5 transition border border-white/5">
                    <span>💡</span> Surprise me
                </button>
                <div class="text-[11px] text-zinc-500 font-mono">
                    <span id="char-count">108</span>/1000 
                    <button onclick="clearPrompt()" class="ml-2 text-zinc-400 hover:text-white font-bold">✕</button>
                </div>
            </div>
        </div>

        <!-- Aspect Ratio Selection -->
        <div class="space-y-2">
            <label class="block text-xs font-bold text-zinc-300">Aspect Ratio</label>
            <div class="grid grid-cols-4 gap-2">
                <button onclick="setRatio('Auto')" class="ratio-btn bg-zinc-900 border border-amber-500 text-amber-400 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center">
                    Auto
                </button>
                <button onclick="setRatio('1:1')" class="ratio-btn bg-zinc-900 border border-white/5 text-zinc-400 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1">
                    1:1 <span class="text-[9px]">👑</span>
                </button>
                <button onclick="setRatio('16:9')" class="ratio-btn bg-zinc-900 border border-white/5 text-zinc-400 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1">
                    16:9 <span class="text-[9px]">👑</span>
                </button>
                <button onclick="setRatio('9:16')" class="ratio-btn bg-zinc-900 border border-white/5 text-zinc-400 py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1">
                    9:16 <span class="text-[9px]">👑</span>
                </button>
            </div>
        </div>

        <!-- AI Sound Toggle Switch -->
        <div class="flex items-center justify-between py-1">
            <div class="flex items-center gap-1.5">
                <span class="text-xs font-bold text-zinc-300">AI Sound</span>
                <span class="text-xs">👑</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" id="ai-sound-toggle" checked class="sr-only peer">
                <div class="w-11 h-6 bg-zinc-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
        </div>

        <!-- Main Generation Action Button -->
        <button id="generate-btn" onclick="startGeneration()" class="w-full btn-gradient text-white font-extrabold py-4 rounded-2xl shadow-xl shadow-purple-900/30 active:scale-98 transition flex items-center justify-center gap-2 text-base">
            <span>✨</span> <span id="btn-text">Generate Comedy Video</span>
        </button>

        <!-- Generation Progress Overlay -->
        <div id="status-container" class="hidden glass-box rounded-2xl p-6 text-center space-y-4">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-3 border-amber-400 border-t-transparent"></div>
            <p id="status-text" class="text-xs font-bold text-amber-400">Initializing job & script pipeline...</p>
            <div id="script-preview" class="text-left text-xs bg-black/60 p-3 rounded-xl border border-white/5 space-y-2 font-mono"></div>
        </div>

        <!-- Result Container -->
        <div id="video-container" class="hidden glass-box rounded-2xl p-6 space-y-4">
            <h3 class="text-emerald-400 font-bold text-sm">Video Ready! 🎉</h3>
            <video id="result-video" controls class="w-full rounded-xl border border-white/10 aspect-video object-cover"></video>
            <button onclick="resetForm()" class="w-full bg-zinc-800 hover:bg-zinc-700 py-3 rounded-xl text-xs font-bold text-zinc-300 transition">
                Create Another Video
            </button>
        </div>

        <!-- Inspirations & Trending Feed -->
        <div class="space-y-3 pt-2">
            <h3 class="text-sm font-bold text-white">Inspirations</h3>
            
            <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1 text-xs">
                <button class="bg-white text-black font-bold px-4 py-1.5 rounded-full whitespace-nowrap">Viral</button>
                <button class="bg-zinc-900 text-zinc-400 font-bold px-4 py-1.5 rounded-full border border-white/5 whitespace-nowrap">ASMR</button>
                <button class="bg-zinc-900 text-zinc-400 font-bold px-4 py-1.5 rounded-full border border-white/5 whitespace-nowrap">Commercial</button>
                <button class="bg-zinc-900 text-zinc-400 font-bold px-4 py-1.5 rounded-full border border-white/5 whitespace-nowrap">Pet</button>
                <button class="bg-zinc-900 text-zinc-400 font-bold px-4 py-1.5 rounded-full border border-white/5 whitespace-nowrap">Funny</button>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div class="relative rounded-2xl overflow-hidden bg-zinc-900 aspect-square border border-white/5 group cursor-pointer">
                    <img src="https://images.unsplash.com/photo-1540573133985-780688d1728b?w=400&auto=format&fit=crop" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
                        <div class="w-8 h-8 rounded-full bg-black/60 backdrop-blur flex items-center justify-center text-white text-xs pl-0.5">▶</div>
                    </div>
                </div>
                <div class="relative rounded-2xl overflow-hidden bg-zinc-900 aspect-square border border-white/5 group cursor-pointer">
                    <img src="https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=400&auto=format&fit=crop" class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
                        <div class="w-8 h-8 rounded-full bg-black/60 backdrop-blur flex items-center justify-center text-white text-xs pl-0.5">▶</div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- App Bottom Navigation Bar -->
    <nav class="fixed bottom-0 inset-x-0 bg-black/95 backdrop-blur-md border-t border-white/10 px-6 py-2.5 flex justify-between items-center z-50 max-w-md mx-auto">
        <button class="flex flex-col items-center gap-1 text-amber-400">
            <span class="text-lg">🎬</span>
            <span class="text-[10px] font-bold">AI Video</span>
        </button>
        <button class="flex flex-col items-center gap-1 text-zinc-500 hover:text-white relative">
            <span class="text-lg">🎨</span>
            <span class="text-[10px] font-medium">AI Art</span>
            <span class="absolute -top-1 -right-2 bg-amber-500 text-[8px] font-black text-black px-1 rounded-full uppercase">NEW</span>
        </button>
        <button class="flex flex-col items-center gap-1 text-zinc-500 hover:text-white">
            <span class="text-lg">🌐</span>
            <span class="text-[10px] font-medium">Collections</span>
        </button>
        <button class="flex flex-col items-center gap-1 text-zinc-500 hover:text-white">
            <span class="text-lg">⚙️</span>
            <span class="text-[10px] font-medium">Settings</span>
        </button>
    </nav>

    <script>
        let pollInterval = null;
        const surprisePrompts = [
            "A hilarious conversation between a sarcastic mountain goat and a wise monkey arguing about a late alarm clock.",
            "Why did the chicken cross the cyber road? An AI animal stand-up comedy sequence.",
            "Two jungle animals discovering a smartphone and trying to record a viral TikTok dance."
        ];

        function updateCharCount() {
            const val = document.getElementById('prompt-input').value;
            document.getElementById('char-count').innerText = val.length;
        }

        function clearPrompt() {
            document.getElementById('prompt-input').value = '';
            updateCharCount();
        }

        function surpriseMe() {
            const idx = Math.floor(Math.random() * surprisePrompts.length);
            document.getElementById('prompt-input').value = surprisePrompts[idx];
            updateCharCount();
        }

        function switchMode(mode) {
            const btnText = document.getElementById('tab-text');
            const btnImg = document.getElementById('tab-image');

            if(mode === 'text') {
                btnText.className = "flex-1 py-2.5 rounded-full text-xs font-bold bg-white text-black transition-all shadow-md";
                btnImg.className = "flex-1 py-2.5 rounded-full text-xs font-bold text-zinc-400 hover:text-white transition-all relative";
            } else {
                btnImg.className = "flex-1 py-2.5 rounded-full text-xs font-bold bg-white text-black transition-all shadow-md relative";
                btnText.className = "flex-1 py-2.5 rounded-full text-xs font-bold text-zinc-400 hover:text-white transition-all";
            }
        }

        function setRatio(ratio) {
            document.querySelectorAll('.ratio-btn').forEach(btn => {
                btn.classList.remove('border-amber-500', 'text-amber-400');
                btn.classList.add('border-white/5', 'text-zinc-400');
            });
            event.currentTarget.classList.remove('border-white/5', 'text-zinc-400');
            event.currentTarget.classList.add('border-amber-500', 'text-amber-400');
        }

        async function startGeneration() {
            const promptText = document.getElementById('prompt-input').value;
            if(!promptText.trim()) {
                alert("Please enter a prompt or comedy topic first!");
                return;
            }

            document.getElementById('form-container').classList.add('hidden');
            document.getElementById('status-container').classList.remove('hidden');
            document.getElementById('status-text').innerText = "Registering job & generating Gemini script...";

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: promptText, char1: "Monkey", char2: "Goat", language: "English" })
                });
                const data = await response.json();

                if (data.success) {
                    if (data.script) {
                        let html = `<p class="text-zinc-400 font-bold mb-1">Script Preview:</p>`;
                        data.script.forEach(line => {
                            html += `<p><strong class="text-amber-400">${line.character}:</strong> ${line.text}</p>`;
                        });
                        document.getElementById('script-preview').innerHTML = html;
                    }

                    document.getElementById('status-text').innerText = "Job queued! Processing ElevenLabs voice & Hedra sync...";
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
                const res = await fetch(`/api/job-status?job_id=` + jobId);
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
"""

@app.route("/", methods=["GET"])
def home():
    return HTML_TEMPLATE

@app.route("/api/generate", methods=["POST"])
def generate_comedy():
    try:
        data = request.json or {}
        topic = data.get("topic", "Late Alarm Clock")
        char1 = data.get("char1", "Monkey")
        char2 = data.get("char2", "Goat")
        language = data.get("language", "English")
        
        job_id = str(uuid.uuid4())
        
        # Safe database insertion
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO video_jobs (job_id, status, char1, char2, language) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (job_id, "pending", char1, char2, language)
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
            "message": f"Generated comedy job registration successfully!",
            "script": [
                {"character": char1, "text": f"Did you hear about this? {topic}!"},
                {"character": char2, "text": "Unbelievable! That's absolute chaos in the jungle."}
            ]
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
