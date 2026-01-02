"""
Text-to-Speech Service
Uses Edge TTS (free Microsoft TTS) to generate voice overs.
"""
import edge_tts
import os
import uuid
from app.core.config import get_settings

settings = get_settings()


class TTSService:
    """Text-to-Speech service using Edge TTS."""
    
    # Indonesian voices
    VOICES = {
        "male": "id-ID-ArdiNeural",
        "female": "id-ID-GadisNeural"
    }
    
    def __init__(self):
        os.makedirs(settings.output_dir, exist_ok=True)
    
    async def generate_audio(
        self, 
        text: str, 
        voice: str = "female",
        video_id: str = None
    ) -> str:
        """
        Generate audio from text.
        
        Args:
            text: The text to convert to speech
            voice: 'male' or 'female'
            video_id: Optional video ID for filename
            
        Returns:
            Path to the generated audio file
        """
        voice_name = self.VOICES.get(voice, self.VOICES["female"])
        
        filename = f"{video_id or uuid.uuid4()}_audio.mp3"
        output_path = os.path.join(settings.output_dir, filename)
        
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_path)
        
        return output_path
    
    async def get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file in seconds."""
        try:
            from moviepy import AudioFileClip
            with AudioFileClip(audio_path) as audio:
                return audio.duration
        except Exception:
            return 10.0  # Default duration


# Singleton instance
tts_service = TTSService()
