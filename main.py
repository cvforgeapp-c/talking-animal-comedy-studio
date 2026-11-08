# main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import shutil

from pipeline import generate_3d_character_video

app = FastAPI(title="Talking Animal & Character Comedy Studio API", version="2.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
job_statuses = {}

@app.post("/api/v1/generate-video")
async def create_video_job(
    background_tasks: BackgroundTasks,
    motion_prompt: str = Form(...),
    character_description: str = Form(default=""),
    reference_image: UploadFile = File(default=None)
):
    job_id = str(uuid.uuid4())
    job_statuses[job_id] = {"status": "processing", "file_path": None}

    image_path = None
    if reference_image:
        image_path = f"uploads/{job_id}_{reference_image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(reference_image.file, buffer)

    def run_job():
        try:
            output_path = generate_3d_character_video(
                character_prompt=character_description,
                motion_prompt=motion_prompt,
                reference_image_path=image_path,
                job_id=job_id
            )
            job_statuses[job_id] = {"status": "completed", "file_path": output_path}
        except Exception as e:
            job_statuses[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(run_job)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Image-to-Video job started with character reference."
    }

@app.get("/api/v1/status/{job_id}")
async def check_status(job_id: str):
    if job_id not in job_statuses:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return job_statuses[job_id]

@app.get("/api/v1/download/{job_id}")
async def download_video(job_id: str):
    if job_id not in job_statuses or job_statuses[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video is not ready or job failed.")
    
    file_path = job_statuses[job_id]["file_path"]
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=f"comedy_sketch_{job_id}.mp4")
    
    raise HTTPException(status_code=404, detail="File not found on server.")
