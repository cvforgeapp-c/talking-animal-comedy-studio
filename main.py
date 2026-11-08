# video-gen-studio/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os

from pipeline import generate_3d_character_video

app = FastAPI(title="Talking Animal & Character Comedy Studio API", version="1.0")

# In-memory job status tracker (use Redis/Celery for production)
job_statuses = {}

class VideoRequest(BaseModel):
    character_description: str
    motion_prompt: str

@app.post("/api/v1/generate-video")
async def create_video_job(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_statuses[job_id] = {"status": "processing", "file_path": None}

    # Run the heavy video generation asynchronously in the background
    def run_job():
        try:
            output_path = generate_3d_character_video(
                request.character_description, 
                request.motion_prompt, 
                job_id
            )
            job_statuses[job_id] = {"status": "completed", "file_path": output_path}
        except Exception as e:
            job_statuses[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(run_job)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Video generation job has started in the background."
    }

@app.get("/api/v1/status/{job_id}")
async def check_status(job_id: str):
    if job_id not in job_statuses:
        raise HTTPException(status_code=404, status_code_detail="Job ID not found")
    return job_statuses[job_id]

@app.get("/api/v1/download/{job_id}")
async def download_video(job_id: str):
    if job_id not in job_statuses or job_statuses[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video is not ready or job failed.")
    
    file_path = job_statuses[job_id]["file_path"]
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=f"comedy_sketch_{job_id}.mp4")
    
    raise HTTPException(status_code=404, detail="File not found on server.")
