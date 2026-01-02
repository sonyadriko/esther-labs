"""
Videos API Router
Handles video generation requests and status queries.
"""
import os
import json
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.models.video import Video, VideoStatus, VideoStyle
from app.schemas.video import VideoResponse, VideoStatusResponse
from app.services import script_generator, tts_service, video_generator

router = APIRouter(prefix="/api/videos", tags=["videos"])
settings = get_settings()


async def process_video_generation(video_id: str, db_url: str):
    """Background task to process video generation with Veo 3 AI."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.services.veo3_generator import veo3_generator
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return
        
        # Step 1: Generate script
        video.status = VideoStatus.GENERATING_SCRIPT.value
        db.commit()
        
        script_sections = await script_generator.generate_script(
            video.product_name,
            video.product_description or "",
            video.style
        )
        video.script = script_sections.get("full_script", "")
        db.commit()
        
        # Step 2: Generate audio (voice over)
        video.status = VideoStatus.GENERATING_AUDIO.value
        db.commit()
        
        audio_path = await tts_service.generate_audio(
            script_sections.get("full_script", ""),
            voice="female",
            video_id=str(video.id)
        )
        video.audio_url = audio_path
        db.commit()
        
        # Step 3: Generate AI video with Veo 3
        video.status = VideoStatus.GENERATING_VIDEO.value
        db.commit()
        
        image_paths = json.loads(video.image_paths) if video.image_paths else []
        
        generated_clips = []
        
        if image_paths:
            # Generate video from each image (max 2 for cost efficiency)
            scene_types = ["intro", "main", "outro"]
            for i, img_path in enumerate(image_paths[:2]):
                scene_type = scene_types[min(i, len(scene_types)-1)]
                
                # Build prompt for this scene
                prompt = veo3_generator.build_product_video_prompt(
                    video.product_name,
                    video.product_description or "",
                    video.style,
                    scene_type
                )
                
                try:
                    clip_path = await veo3_generator.generate_video_from_image(
                        image_path=img_path,
                        prompt=prompt,
                        video_id=f"{video.id}_{i}",
                        aspect_ratio="9:16",
                        duration_seconds=4  # 4 seconds per clip to save cost
                    )
                    generated_clips.append(clip_path)
                except Exception as e:
                    print(f"Veo 3 generation failed for clip {i}: {e}")
                    # Fallback to MoviePy slideshow for this clip
                    fallback_path = await video_generator.generate_video(
                        video_id=f"{video.id}_{i}_fallback",
                        image_paths=[img_path],
                        audio_path=audio_path,
                        script_sections={"hook": script_sections.get("hook", "")},
                        style=video.style
                    )
                    generated_clips.append(fallback_path)
        else:
            # Text-to-video only (no image)
            prompt = veo3_generator.build_product_video_prompt(
                video.product_name,
                video.product_description or "",
                video.style,
                "main"
            )
            
            try:
                clip_path = await veo3_generator.generate_video_from_text(
                    prompt=prompt,
                    video_id=str(video.id),
                    aspect_ratio="9:16",
                    duration_seconds=8
                )
                generated_clips.append(clip_path)
            except Exception as e:
                print(f"Text-to-video failed: {e}")
                # Fallback
                fallback_path = await video_generator.generate_video(
                    video_id=str(video.id),
                    image_paths=[],
                    audio_path=audio_path,
                    script_sections=script_sections,
                    style=video.style
                )
                generated_clips.append(fallback_path)
        
        # Step 4: Combine clips and add audio
        if len(generated_clips) == 1:
            final_video_path = generated_clips[0]
        else:
            # Concatenate multiple clips
            clips = [VideoFileClip(p) for p in generated_clips]
            combined = concatenate_videoclips(clips, method="compose")
            
            final_video_path = os.path.join(settings.output_dir, f"{video.id}_combined.mp4")
            combined.write_videofile(
                final_video_path, 
                codec="libx264",
                audio_codec="aac",
                fps=30
            )
            
            # Cleanup
            for clip in clips:
                clip.close()
            combined.close()
        
        # Add voice over to final video
        try:
            video_clip = VideoFileClip(final_video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # If audio is longer than video, trim audio
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclipped(0, video_clip.duration)
            
            # If video is longer than audio, that's fine (silent end)
            final_with_audio = video_clip.with_audio(audio_clip)
            
            output_path = os.path.join(settings.output_dir, f"{video.id}.mp4")
            final_with_audio.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=30
            )
            
            video_clip.close()
            audio_clip.close()
            final_with_audio.close()
            
            video.video_url = output_path
        except Exception as e:
            print(f"Audio merge failed: {e}")
            video.video_url = final_video_path
        
        video.status = VideoStatus.DONE.value
        
        # Create thumbnail
        if image_paths:
            thumb_path = await video_generator.create_thumbnail(
                image_paths[0], 
                str(video.id)
            )
            video.thumbnail_url = thumb_path
        
        db.commit()
        
    except Exception as e:
        video.status = VideoStatus.FAILED.value
        video.error_message = str(e)
        db.commit()
        print(f"Video generation failed: {e}")
    finally:
        db.close()



@router.post("", response_model=VideoResponse)
async def create_video(
    background_tasks: BackgroundTasks,
    product_name: str = Form(...),
    product_description: str = Form(None),
    style: str = Form("minimal"),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new video generation request.
    
    - **product_name**: Name of the product
    - **product_description**: Description and key features
    - **style**: Video style (luxury, minimal, tech, lifestyle)
    - **images**: Product images (optional, up to 3)
    """
    # Validate style
    try:
        video_style = VideoStyle(style)
    except ValueError:
        video_style = VideoStyle.MINIMAL
    
    # Save uploaded images
    image_paths = []
    if images:
        os.makedirs(settings.upload_dir, exist_ok=True)
        for i, img in enumerate(images[:3]):  # Max 3 images
            if img.filename:
                ext = os.path.splitext(img.filename)[1] or ".jpg"
                filename = f"{uuid.uuid4()}{ext}"
                filepath = os.path.join(settings.upload_dir, filename)
                
                with open(filepath, "wb") as f:
                    content = await img.read()
                    f.write(content)
                
                image_paths.append(filepath)
    
    # Create video record
    video = Video(
        product_name=product_name,
        product_description=product_description,
        style=video_style.value,
        status=VideoStatus.PENDING.value,
        image_paths=json.dumps(image_paths) if image_paths else None
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Start background processing
    background_tasks.add_task(
        process_video_generation,
        str(video.id),
        settings.database_url
    )
    
    return video


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get video details by ID."""
    try:
        vid = uuid.UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    video = db.query(Video).filter(Video.id == vid).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    """Get video generation status."""
    try:
        vid = uuid.UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    video = db.query(Video).filter(Video.id == vid).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Progress messages
    progress_messages = {
        VideoStatus.PENDING.value: "Menunggu proses...",
        VideoStatus.PROCESSING.value: "Memproses...",
        VideoStatus.GENERATING_SCRIPT.value: "Membuat script review...",
        VideoStatus.GENERATING_AUDIO.value: "Membuat voice over...",
        VideoStatus.GENERATING_VIDEO.value: "Membuat video...",
        VideoStatus.DONE.value: "Video siap!",
        VideoStatus.FAILED.value: "Gagal membuat video"
    }
    
    return VideoStatusResponse(
        id=video.id,
        status=video.status,
        video_url=video.video_url,
        error_message=video.error_message,
        progress_message=progress_messages.get(video.status, "")
    )


@router.get("/{video_id}/download")
async def download_video(video_id: str, db: Session = Depends(get_db)):
    """Download the generated video."""
    try:
        vid = uuid.UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")
    
    video = db.query(Video).filter(Video.id == vid).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status != VideoStatus.DONE.value:
        raise HTTPException(status_code=400, detail="Video is not ready yet")
    
    if not video.video_url or not os.path.exists(video.video_url):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video.video_url,
        media_type="video/mp4",
        filename=f"{video.product_name.replace(' ', '_')}_review.mp4"
    )
