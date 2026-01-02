"""
Veo 3 Video Generator Service
Uses Google Veo 3 API for AI video generation from images.
"""
import os
import time
import base64
import httpx
import asyncio
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


class Veo3VideoGenerator:
    """Generate AI videos using Google Veo 3."""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        os.makedirs(settings.output_dir, exist_ok=True)
    
    async def generate_video_from_image(
        self,
        image_path: str,
        prompt: str,
        video_id: str,
        aspect_ratio: str = "9:16",
        duration_seconds: int = 8
    ) -> str:
        """
        Generate a video from an image using Veo 3.
        
        Args:
            image_path: Path to the source image
            prompt: Text prompt describing the video motion
            video_id: Unique ID for output file
            aspect_ratio: "9:16" for vertical, "16:9" for horizontal
            duration_seconds: 4, 6, or 8 seconds
            
        Returns:
            Path to the generated video file
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        
        # Determine mime type
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/jpeg")
        
        # Create generation request
        url = f"{self.BASE_URL}/models/veo-3.0-generate-preview:predictLongRunning"
        
        payload = {
            "instances": [
                {
                    "prompt": prompt,
                    "image": {
                        "bytesBase64Encoded": image_data,
                        "mimeType": mime_type
                    }
                }
            ],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration_seconds,
                "personGeneration": "dont_allow",
                "numberOfVideos": 1
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=300) as client:
            # Start generation
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.json() if response.content else response.text
                raise Exception(f"Veo 3 API error: {response.status_code} - {error_detail}")
            
            result = response.json()
            operation_name = result.get("name")
            
            if not operation_name:
                raise Exception("No operation name returned from Veo 3")
            
            # Poll for completion
            video_data = await self._poll_operation(client, operation_name, headers)
            
            # Save video
            output_path = os.path.join(settings.output_dir, f"{video_id}_veo.mp4")
            video_bytes = base64.standard_b64decode(video_data)
            
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            
            return output_path
    
    async def generate_video_from_text(
        self,
        prompt: str,
        video_id: str,
        aspect_ratio: str = "9:16",
        duration_seconds: int = 8
    ) -> str:
        """
        Generate a video from text prompt only using Veo 3.
        
        Args:
            prompt: Text prompt describing the video
            video_id: Unique ID for output file
            aspect_ratio: "9:16" for vertical, "16:9" for horizontal
            duration_seconds: 4, 6, or 8 seconds
            
        Returns:
            Path to the generated video file
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured")
        
        url = f"{self.BASE_URL}/models/veo-3.0-generate-preview:predictLongRunning"
        
        payload = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration_seconds,
                "personGeneration": "dont_allow",
                "numberOfVideos": 1
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.json() if response.content else response.text
                raise Exception(f"Veo 3 API error: {response.status_code} - {error_detail}")
            
            result = response.json()
            operation_name = result.get("name")
            
            if not operation_name:
                raise Exception("No operation name returned from Veo 3")
            
            video_data = await self._poll_operation(client, operation_name, headers)
            
            output_path = os.path.join(settings.output_dir, f"{video_id}_veo.mp4")
            video_bytes = base64.standard_b64decode(video_data)
            
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            
            return output_path
    
    async def _poll_operation(
        self, 
        client: httpx.AsyncClient, 
        operation_name: str, 
        headers: dict,
        max_wait: int = 300
    ) -> str:
        """Poll long-running operation until complete."""
        url = f"{self.BASE_URL}/{operation_name}"
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait:
                raise TimeoutError("Veo 3 video generation timed out")
            
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to poll operation: {response.status_code}")
            
            result = response.json()
            
            if result.get("done"):
                # Check for error
                if "error" in result:
                    raise Exception(f"Veo 3 generation failed: {result['error']}")
                
                # Extract video data
                response_data = result.get("response", {})
                generated_videos = response_data.get("generatedVideos", [])
                
                if not generated_videos:
                    raise Exception("No videos generated")
                
                video_data = generated_videos[0].get("video", {}).get("bytesBase64Encoded")
                
                if not video_data:
                    raise Exception("No video data in response")
                
                return video_data
            
            # Wait before next poll
            await asyncio.sleep(5)
    
    def build_product_video_prompt(
        self,
        product_name: str,
        product_description: str,
        style: str,
        scene_type: str = "main"
    ) -> str:
        """Build an optimized prompt for product video generation."""
        
        style_descriptions = {
            "luxury": "elegant, premium, golden lighting, slow smooth motion, luxurious atmosphere, high-end commercial quality",
            "minimal": "clean, modern, soft white lighting, gentle floating motion, minimalist aesthetic, professional product shot",
            "tech": "futuristic, neon blue accents, dynamic rotation, tech commercial style, sleek and innovative",
            "lifestyle": "warm, inviting, natural lighting, lifestyle setting, friendly and approachable"
        }
        
        style_desc = style_descriptions.get(style, style_descriptions["minimal"])
        
        scene_prompts = {
            "intro": f"Cinematic opening shot of {product_name}, slowly emerging from darkness, {style_desc}, dramatic reveal",
            "main": f"Product showcase of {product_name}, smooth 360-degree rotation, {style_desc}, commercial quality, studio lighting",
            "detail": f"Close-up detail shot of {product_name}, highlighting texture and quality, {style_desc}, macro lens effect",
            "outro": f"Final hero shot of {product_name}, floating elegantly, {style_desc}, fade to subtle glow"
        }
        
        base_prompt = scene_prompts.get(scene_type, scene_prompts["main"])
        
        # Add product context
        if product_description:
            base_prompt += f", {product_description[:100]}"
        
        return base_prompt


# Singleton instance
veo3_generator = Veo3VideoGenerator()
