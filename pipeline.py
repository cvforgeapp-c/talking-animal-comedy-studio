# pipeline.py
import torch
import os
from diffusers import AutoPipelineForText2Image, LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip

os.makedirs("outputs", exist_ok=True)
os.makedirs("temp_audio", exist_ok=True)

def generate_3d_character_video(
    character_prompt: str, 
    motion_prompt: str, 
    dialogue_script: str, 
    reference_image_path: str, 
    job_id: str
):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        # 1. Keyframe generation (Image-to-Video or Text-to-Image)
        if reference_image_path and os.path.exists(reference_image_path):
            print(f"[{job_id}] Using reference image for character consistency.")
            keyframe_path = reference_image_path
        else:
            print(f"[{job_id}] Generating 3D character keyframe via Flux...")
            t2i_pipe = AutoPipelineForText2Image.from_pretrained(
                "black-forest-labs/FLUX.1-schnell",
                torch_dtype=torch.bfloat16
            ).to(device)

            full_prompt = f"3D animation render, Pixar style, highly detailed character. {character_prompt}. Subsurface scattering, cinematic studio lighting."
            keyframe_image = t2i_pipe(prompt=full_prompt, height=1280, width=720, num_inference_steps=4).images[0]
            
            keyframe_path = f"outputs/{job_id}_keyframe.png"
            keyframe_image.save(keyframe_path)

            del t2i_pipe
            torch.cuda.empty_cache()

        # 2. Animate Keyframe (Image-to-Video)
        print(f"[{job_id}] Loading LTX-Video pipeline...")
        i2v_pipe = LTXImageToVideoPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            torch_dtype=torch.bfloat16
        ).to(device)
        i2v_pipe.enable_model_cpu_offload()

        full_motion_prompt = f"{motion_prompt}, cinematic 3D animated style, expressive mouth movements."
        video_frames = i2v_pipe(
            image=load_image(keyframe_path),
            prompt=full_motion_prompt,
            num_inference_steps=30,
            num_frames=97
        ).frames[0]

        silent_video_path = f"outputs/{job_id}_silent.mp4"
        export_to_video(video_frames, silent_video_path, fps=24)
        del i2v_pipe
        torch.cuda.empty_cache()

        # 3. Generate Speech Audio (TTS) & Merge with Video
        final_output_path = f"outputs/{job_id}_output.mp4"
        if dialogue_script and dialogue_script.strip():
            print(f"[{job_id}] Synthesizing voice dialogue...")
            audio_path = f"temp_audio/{job_id}.mp3"
            tts = gTTS(text=dialogue_script, lang='en', slow=False)
            tts.save(audio_path)

            print(f"[{job_id}] Merging audio track into video...")
            video_clip = VideoFileClip(silent_video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Loop or trim audio to match video duration if needed, or set audio
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac", fps=24)
            
            # Clean up temp files
            video_clip.close()
            audio_clip.close()
            if os.path.exists(silent_video_path):
                os.remove(silent_video_path)
        else:
            # If no dialogue, just rename silent video to final output
            os.rename(silent_video_path, final_output_path)

        print(f"[{job_id}] Talking video successfully completed at {final_output_path}")
        return final_output_path

    except Exception as e:
        print(f"[{job_id}] Error in pipeline: {str(e)}")
        raise e
