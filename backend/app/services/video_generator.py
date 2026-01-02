"""
Video Generator Service
Creates product review videos using MoviePy and PIL.
"""
import os
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (
    ImageClip, 
    AudioFileClip, 
    TextClip, 
    CompositeVideoClip,
    concatenate_videoclips
)
from app.core.config import get_settings

settings = get_settings()


class VideoGenerator:
    """Generate product review videos."""
    
    STYLE_CONFIGS = {
        "luxury": {
            "bg_color": (20, 20, 30),
            "text_color": (212, 175, 55),  # Gold
            "accent_color": (255, 215, 0),
            "font_size": 48,
        },
        "minimal": {
            "bg_color": (250, 250, 250),
            "text_color": (30, 30, 30),
            "accent_color": (100, 100, 100),
            "font_size": 44,
        },
        "tech": {
            "bg_color": (15, 15, 25),
            "text_color": (0, 255, 200),
            "accent_color": (100, 200, 255),
            "font_size": 46,
        },
        "lifestyle": {
            "bg_color": (255, 245, 238),
            "text_color": (60, 60, 60),
            "accent_color": (255, 150, 150),
            "font_size": 42,
        },
    }
    
    def __init__(self):
        os.makedirs(settings.output_dir, exist_ok=True)
        os.makedirs(settings.upload_dir, exist_ok=True)
    
    async def generate_video(
        self,
        video_id: str,
        image_paths: list[str],
        audio_path: str,
        script_sections: dict,
        style: str = "minimal"
    ) -> str:
        """
        Generate a product review video.
        
        Args:
            video_id: Unique ID for the video
            image_paths: List of product image paths
            audio_path: Path to the audio file
            script_sections: Dict with 'hook', 'benefits', 'cta' text
            style: Video style
            
        Returns:
            Path to the generated video file
        """
        config = self.STYLE_CONFIGS.get(style, self.STYLE_CONFIGS["minimal"])
        
        # Get audio duration
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        # Calculate duration per scene
        num_scenes = min(len(image_paths), 3) if image_paths else 1
        scene_duration = total_duration / num_scenes
        
        clips = []
        texts = [script_sections.get("hook", ""), 
                 script_sections.get("benefits", ""),
                 script_sections.get("cta", "")]
        
        for i in range(num_scenes):
            # Create scene
            if image_paths and i < len(image_paths):
                scene = self._create_product_scene(
                    image_paths[i], 
                    texts[i] if i < len(texts) else "",
                    config,
                    scene_duration
                )
            else:
                scene = self._create_text_scene(
                    texts[i] if i < len(texts) else "Product Review",
                    config,
                    scene_duration
                )
            clips.append(scene)
        
        # Concatenate all clips
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        final_video = final_video.with_audio(audio_clip)
        
        # Export
        output_path = os.path.join(settings.output_dir, f"{video_id}.mp4")
        final_video.write_videofile(
            output_path,
            fps=settings.video_fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium"
        )
        
        # Cleanup
        audio_clip.close()
        final_video.close()
        for clip in clips:
            clip.close()
        
        return output_path
    
    def _create_product_scene(
        self, 
        image_path: str, 
        text: str, 
        config: dict,
        duration: float
    ) -> ImageClip:
        """Create a scene with product image and text overlay."""
        # Create background
        bg = Image.new('RGB', (settings.video_width, settings.video_height), config["bg_color"])
        
        # Load and resize product image
        try:
            product_img = Image.open(image_path)
            # Calculate size to fit in frame with padding
            max_size = min(settings.video_width - 100, settings.video_height - 400)
            product_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Center product image
            x = (settings.video_width - product_img.width) // 2
            y = (settings.video_height - product_img.height) // 2 - 100
            
            # Add shadow effect
            shadow = Image.new('RGBA', product_img.size, (0, 0, 0, 100))
            bg.paste(shadow, (x + 10, y + 10), shadow if shadow.mode == 'RGBA' else None)
            
            # Paste product image
            if product_img.mode == 'RGBA':
                bg.paste(product_img, (x, y), product_img)
            else:
                bg.paste(product_img, (x, y))
        except Exception as e:
            print(f"Error loading image: {e}")
        
        # Add text at bottom
        if text:
            bg = self._add_text_overlay(bg, text, config, position="bottom")
        
        # Convert to clip
        bg_path = os.path.join(settings.output_dir, f"temp_{uuid.uuid4()}.png")
        bg.save(bg_path)
        
        clip = ImageClip(bg_path).with_duration(duration)
        
        # Cleanup temp file
        try:
            os.remove(bg_path)
        except:
            pass
        
        return clip
    
    def _create_text_scene(
        self, 
        text: str, 
        config: dict,
        duration: float
    ) -> ImageClip:
        """Create a scene with text only."""
        bg = Image.new('RGB', (settings.video_width, settings.video_height), config["bg_color"])
        
        if text:
            bg = self._add_text_overlay(bg, text, config, position="center")
        
        bg_path = os.path.join(settings.output_dir, f"temp_{uuid.uuid4()}.png")
        bg.save(bg_path)
        
        clip = ImageClip(bg_path).with_duration(duration)
        
        try:
            os.remove(bg_path)
        except:
            pass
        
        return clip
    
    def _add_text_overlay(
        self, 
        image: Image.Image, 
        text: str, 
        config: dict,
        position: str = "bottom"
    ) -> Image.Image:
        """Add text overlay to image."""
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", config["font_size"])
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", config["font_size"])
            except:
                font = ImageFont.load_default()
        
        # Word wrap text
        words = text.split()
        lines = []
        current_line = []
        max_width = settings.video_width - 100
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate text position
        line_height = config["font_size"] + 10
        total_text_height = len(lines) * line_height
        
        if position == "bottom":
            y_start = settings.video_height - total_text_height - 150
        elif position == "top":
            y_start = 100
        else:  # center
            y_start = (settings.video_height - total_text_height) // 2
        
        # Draw text with shadow
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (settings.video_width - text_width) // 2
            y = y_start + i * line_height
            
            # Shadow
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0))
            # Main text
            draw.text((x, y), line, font=font, fill=config["text_color"])
        
        return image
    
    async def create_thumbnail(self, image_path: str, video_id: str) -> str:
        """Create a thumbnail from the first product image."""
        try:
            img = Image.open(image_path)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            thumb_path = os.path.join(settings.output_dir, f"{video_id}_thumb.jpg")
            img.save(thumb_path, "JPEG", quality=85)
            
            return thumb_path
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return ""


# Singleton instance
video_generator = VideoGenerator()
