"""
GPU/CPU detection utility for Whisper transcription
"""

import subprocess
from typing import Tuple


def get_device_info() -> Tuple[str, str]:
    """
    Get device information for processing
    
    Returns:
        Tuple of (device_name, device_type)
        device_name: Human-readable device name
        device_type: "cuda" or "cpu"
    """
    try:
        # Check if nvidia-smi is available and CUDA is working
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            device_name = result.stdout.strip().split('\n')[0]
            return f"GPU: {device_name}", "cuda"
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    return "CPU", "cpu"


def get_device() -> str:
    """
    Get the device string for faster-whisper operations
    
    Returns:
        "cuda" if GPU is available, "cpu" otherwise
    """
    _, device_type = get_device_info()
    return device_type