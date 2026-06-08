import os
import re
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
from app.config import TESSERACT_CMD, DEFAULT_LANGUAGES
from app.utils import logger

# Set the Tesseract binary path
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    logger.info(f"Tesseract command path configured: {TESSERACT_CMD}")

class OCRExtractorError(Exception):
    """Custom exception for OCR processing errors."""
    pass

class TesseractNotInstalledError(OCRExtractorError):
    """Raised when Tesseract OCR engine is not installed or not in PATH."""
    pass

class LanguagePackMissingError(OCRExtractorError):
    """Raised when the requested Tesseract language pack is missing."""
    pass

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Applies preprocessing to improve OCR accuracy:
    1. Detects and corrects image rotation/orientation using OSD.
    2. Converts image to grayscale.
    3. Applies autocontrast to handle low lighting and uneven reflections.
    4. Resizes the image if it is too small (Tesseract performs better on larger text).
    5. Enhances contrast.
    6. Enhances sharpness to reduce camera blur.
    """
    try:
        # 1. Orientation / Rotation correction using OSD
        try:
            osd = pytesseract.image_to_osd(image)
            rotation = re.search(r'Rotate: (\d+)', osd)
            if rotation:
                angle = int(rotation.group(1))
                if angle != 0:
                    logger.info(f"Correcting image rotation: rotating by {angle} degrees")
                    image = image.rotate(-angle, expand=True)
        except Exception as osd_err:
            logger.debug(f"Orientation detection skipped: {str(osd_err)}")

        # 2. Convert to grayscale
        gray = image.convert('L')
        
        # 3. Apply autocontrast
        gray = ImageOps.autocontrast(gray)
        
        # 4. Resize if width or height is less than 1200px
        width, height = gray.size
        if width < 1200 or height < 1200:
            scale_factor = 2
            gray = gray.resize((width * scale_factor, height * scale_factor), Image.Resampling.LANCZOS)
            
        # 5. Enhance Contrast
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(2.0)
        
        # 6. Enhance Sharpness to reduce camera blur
        sharpness_enhancer = ImageEnhance.Sharpness(gray)
        enhanced = sharpness_enhancer.enhance(2.0)
        
        return enhanced
    except Exception as e:
        logger.warning(f"Image preprocessing failed, proceeding with original: {str(e)}")
        return image

def extract_text_from_image(image_path_or_file, lang: str = None) -> str:
    """
    Opens an image, preprocesses it, and extracts text using Tesseract OCR.
    
    Args:
        image_path_or_file: A path to an image file or a file-like object.
        lang: Tesseract language codes (e.g. 'eng+guj'). Defaults to DEFAULT_LANGUAGES.
        
    Returns:
        The extracted raw text string.
    """
    if lang is None:
        lang = DEFAULT_LANGUAGES

    try:
        # Open the image using Pillow
        with Image.open(image_path_or_file) as img:
            # We copy to avoid closed file issues if processing in memory
            img_copy = img.copy()
            
        # Preprocess the image
        processed_img = preprocess_image(img_copy)
        
        logger.info(f"Running OCR with languages: '{lang}'")
        
        # Execute Tesseract OCR
        raw_text = pytesseract.image_to_string(processed_img, lang=lang)
        return raw_text
        
    except pytesseract.TesseractNotFoundError:
        error_msg = (
            "Tesseract OCR executable not found. Please install Tesseract OCR "
            "and make sure it is configured correctly in PATH or config.py."
        )
        logger.error(error_msg)
        raise TesseractNotInstalledError(error_msg)
        
    except pytesseract.TesseractError as e:
        err_str = str(e)
        logger.error(f"Tesseract execution error: {err_str}")
        
        # Check if error is related to missing language packs
        if "Error opening data file" in err_str or "Failed loading language" in err_str:
            missing_lang_msg = (
                f"Tesseract language pack missing for '{lang}'. Please install "
                f"the appropriate language packs (e.g. 'guj.traineddata' for Gujarati)."
            )
            raise LanguagePackMissingError(missing_lang_msg)
            
        raise OCRExtractorError(f"Failed to extract text using Tesseract: {err_str}")
        
    except Exception as e:
        error_msg = f"Unexpected error during OCR processing: {str(e)}"
        logger.error(error_msg)
        raise OCRExtractorError(error_msg)
