# video-gen-studio/pipeline.py
import torch
import os
from diffusers import AutoPipelineForText2Image, LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

def generate_3d_character_video(character_prompt: str, motion_prompt: str, job_id: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("Warning: Running on CPU. Video generation will be extremely slow.")

    try:
        # -------------------------------------------------------------
        # 1. STEP 1: Generate 3D Character Keyframe (Text-to-Image)
        # -------------------------------------------------------------
        print(f"[{job_id}] Loading Text-to-Image pipeline...")
        t2i_pipe = AutoPipelineForText2Image.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        ).to(device)

        full_character_prompt = (
            f"3D animation render, Pixar style, highly detailed character. {character_prompt}. "
            "Subsurface scattering, expressive features, 8k cinematic render, studio lighting."
        )

        print(f"[{job_id}] Generating 3D keyframe...")
        keyframe_image = t2i_pipe(
            prompt=full_character_prompt,
            height=1280,
            width=720,
            num_inference_steps=4
        ).images[0]

        keyframe_path = f"outputs/{job_id}_keyframe.png"
        keyframe_image.save(keyframe_path)

        # Free VRAM before loading the video model
        del t2i_pipe
        torch.cuda.empty_cache()

        # -------------------------------------------------------------
        # 2. STEP 2: Animate Keyframe (Image-to-Video)
        # -------------------------------------------------------------
        print(f"[{job_id}] Loading Image-to-Video pipeline...")
        i2v_pipe = LTXImageToVideoPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            torch_dtype=torch.bfloat16
        ).to(device)

        i2v_pipe.enable_model_cpu_offload()

        full_motion_prompt = f"{motion_prompt}, cinematic camera motion, 3D animated style."

        print(f"[{job_id}] Generating video clip...")
        video_frames = i2v_pipe(
            image=load_image(keyframe_path),
            prompt=full_motion_prompt,
            num_inference_steps=30,
            num_frames=97  # ~4 seconds of video
        ).frames[0]

        output_video_path = f"outputs/{job_id}_output.mp4"
        export_to_video(video_frames, output_video_path, fps=24)
        print(f"[{job_id}] Video successfully generated at {output_video_path}")

        return output_video_path

    except Exception as e:
        print(f"[{job_id}] Error during generation: {str(e)}")
        raise e
