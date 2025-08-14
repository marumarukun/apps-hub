"""
Whisper GPU Transcription App for CloudRun deployment
"""

import gradio as gr
from src.core.whisper_service import WhisperService
from src.utils.device import get_device_info
from src.utils.logger import logger


def create_app():
    """Create and configure the Gradio app"""
    
    # Initialize WhisperService
    whisper_service = WhisperService()
    device_name, device_type = get_device_info()
    
    # Load model on startup
    load_status = whisper_service.load_model("base")
    logger.info(f"Model load status: {load_status}")
    
    def transcribe_with_progress(audio_file, progress=gr.Progress()):
        """Transcribe audio file with progress tracking"""
        if audio_file is None:
            return "❌ Please upload an audio file first."
        
        return whisper_service.transcribe_audio(audio_file, progress)
    
    # Create Gradio interface
    with gr.Blocks(title="Whisper GPU Transcription") as app:
        gr.Markdown("# 🎙️ Whisper GPU Transcription")
        
        # Device status display
        device_status = gr.Markdown(f"🖥️ **Current Device**: {device_name}")
        
        gr.Markdown("Upload an audio file to transcribe using Whisper.")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    sources=["upload"],
                    type="filepath",
                    label="Audio File",
                    format="wav"
                )
                transcribe_btn = gr.Button("🎯 Transcribe", variant="primary", size="lg")
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="Transcription Result",
                    lines=10,
                    max_lines=20,
                    show_copy_button=True
                )
        
        # Set up event handlers
        transcribe_btn.click(
            fn=transcribe_with_progress,
            inputs=[audio_input],
            outputs=[output_text],
            show_progress=True
        )
        
        # Also allow transcription by uploading file
        audio_input.change(
            fn=transcribe_with_progress,
            inputs=[audio_input],
            outputs=[output_text],
            show_progress=True
        )
    
    return app


if __name__ == "__main__":
    logger.info("Starting Whisper GPU Transcription app")
    app = create_app()
    app.launch(
        server_name="0.0.0.0", 
        server_port=8080,
        show_error=True
    )
