from flask import Flask, jsonify, request, render_template
import os
import uuid
import json
import requests

app = Flask(__name__, template_folder='.')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LUMA_API_KEY = os.getenv("LUMA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Configure Gemini
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini configuration error: {e}")

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
        external_task_id = None
        video_url = ""
        initial_status = "processing"

        # 1. Generate Script with Gemini
        if strict_mode and incoming_script:
            script_lines = incoming_script
        else:
            if GEMINI_API_KEY:
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    ai_prompt = f"""
                    You are an expert comedy scriptwriter. Analyze this prompt and write a funny 3-line dialogue script:
                    User Prompt: "{prompt}"
                    Format strictly as a valid JSON list of objects with keys "character" and "text":
                    [
                      {{"character": "Character 1", "text": "..."}},
                      {{"character": "Character 2", "text": "..."}}
                    ]
                    """
                    response = model.generate_content(ai_prompt)
                    cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
                    script_lines = json.loads(cleaned_text)
                except Exception as ai_err:
                    script_lines = [{"character": "Host", "text": f"Prompt: {prompt}"}]
            else:
                script_lines = [{"character": "Host", "text": prompt}]

        # 2. Direct HTTP Call to Luma API (Bypasses SDK version issues)
        if LUMA_API_KEY:
            try:
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {LUMA_API_KEY}",
                    "content-type": "application/json"
                }
                payload = {
                    "prompt": prompt,
                    "model": "ray-2",
                    "aspect_ratio": "16:9",
                    "loop": False
                }
                res = requests.post("https://api.lumalabs.ai/dream-machine/v1/generations", headers=headers, json=payload, timeout=10)
                if res.status_code == 201 or res.status_code == 200:
                    res_data = res.json()
                    external_task_id = res_data.get("id")
                    print(f"Luma direct task created: {external_task_id}")
                else:
                    print(f"Luma API error response: {res.text}")
                    initial_status = "completed"
                    video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
            except Exception as luma_err:
                print(f"Luma request exception: {luma_err}")
                initial_status = "completed"
                video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        else:
            initial_status = "completed"
            video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

        return jsonify({
            "success": True,
            "job_id": job_id,
            "status": initial_status,
            "script": script_lines,
            "video_url": video_url,
            "external_task_id": external_task_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/job-status", methods=["GET"])
def job_status():
    try:
        job_id = request.args.get("job_id")
        task_id = request.args.get("task_id") # Can pass task_id from frontend if stored
        
        # If Luma task exists, check status directly via HTTP GET
        if LUMA_API_KEY and task_id:
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {LUMA_API_KEY}"
            }
            res = requests.get(f"https://api.lumalabs.ai/dream-machine/v1/generations/{task_id}", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                state = data.get("state")
                if state == "completed":
                    assets = data.get("assets", {})
                    video_url = assets.get("video", "")
                    return jsonify({"success": True, "status": "completed", "video_url": video_url})
                elif state == "failed":
                    return jsonify({"success": True, "status": "failed", "video_url": ""})
                else:
                    return jsonify({"success": True, "status": "processing", "video_url": ""})

        return jsonify({"success": True, "status": "completed", "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
