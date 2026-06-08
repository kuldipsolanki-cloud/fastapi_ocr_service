import os
import sys
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure Tesseract to search our local workspace tessdata folder
# TESSDATA_PREFIX should point directly to the 'tessdata' folder containing the *.traineddata files
os.environ["TESSDATA_PREFIX"] = str(BASE_DIR / "tessdata")

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# CORS Origins - default to '*' (all) for easy mobile/web development,
# but can be customized via environment variables.
CORS_ORIGINS = [
    origin.strip() 
    for origin in os.getenv("CORS_ORIGINS", "*").split(",") 
    if origin.strip()
]

# Tesseract Configuration
# Standard search paths for Windows
WINDOWS_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

def get_tesseract_cmd() -> str:
    """
    Resolves the Tesseract executable path.
    Checks environment variable first, then standard paths on Windows, and falls back to system path on Unix.
    """
    env_path = os.getenv("TESSERACT_CMD")
    if env_path:
        return env_path
    
    # If on Windows, check default install locations
    if sys.platform.startswith("win"):
        for path in WINDOWS_TESSERACT_PATHS:
            if os.path.exists(path):
                return path
        # Fallback if not found in standard paths but maybe added to system PATH
        return "tesseract.exe"
        
    # Linux / macOS fallback (usually resolved globally via PATH)
    return "tesseract"

TESSERACT_CMD = get_tesseract_cmd()
DEFAULT_LANGUAGES = os.getenv("DEFAULT_LANGUAGES", "eng+guj+hin")
