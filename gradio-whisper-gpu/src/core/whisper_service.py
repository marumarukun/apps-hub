"""
Whisper transcription service using faster-whisper
"""

from faster_whisper import WhisperModel
from typing import Optional
import gradio as gr
from src.utils.device import get_device, get_device_info
from src.utils.logger import logger


class WhisperService:
    def __init__(self):
        self.model: Optional[WhisperModel] = None
        self.device = get_device()
        self.device_name, _ = get_device_info()
        logger.info(f"Initialized WhisperService with device: {self.device_name}")
    
    def load_model(self, model_name: str = "base"):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model '{model_name}' on {self.device_name}")
            # Use faster-whisper which supports GPU acceleration
            compute_type = "float16" if self.device == "cuda" else "int8"
            self.model = WhisperModel(
                model_name, 
                device=self.device,
                compute_type=compute_type,
                local_files_only=False
            )
            logger.info(f"Model loaded successfully on {self.device_name}")
            return f"✅ Model loaded on {self.device_name}"
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return f"❌ Failed to load model: {str(e)}"
    
    def transcribe_audio(self, audio_file_path: str, progress: gr.Progress) -> str:
        """Transcribe audio file"""
        if self.model is None:
            return "❌ Model not loaded. Please load model first."
        
        try:
            logger.info(f"Starting transcription of {audio_file_path}")
            progress(0.1, desc="Loading audio file...")
            
            # Transcribe with progress updates
            progress(0.3, desc="Processing audio...")
            segments, info = self.model.transcribe(
                audio_file_path, 
                language=None,  # Auto-detect language
                beam_size=5
            )
            
            progress(0.7, desc="Extracting text...")
            # Collect all transcribed text
            transcribed_text = ""
            for segment in segments:
                transcribed_text += segment.text
            
            progress(1.0, desc="Transcription complete!")
            logger.info("Transcription completed successfully")
            
            detected_language = info.language if hasattr(info, 'language') else "Unknown"
            
            return f"🎯 **Device**: {self.device_name}\n🌍 **Language**: {detected_language}\n\n📝 **Transcription**:\n{transcribed_text.strip()}"
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return f"❌ Transcription failed: {str(e)}"