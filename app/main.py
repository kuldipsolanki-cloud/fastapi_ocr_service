import io
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.config import HOST, PORT, DEBUG, CORS_ORIGINS, DEFAULT_LANGUAGES
from app.utils import logger
from app.ocr import (
    extract_text_from_image, 
    TesseractNotInstalledError, 
    LanguagePackMissingError, 
    OCRExtractorError
)
from app.parser import parse_business_card
import pytesseract

# FastAPI Initialization
app = FastAPI(
    title="Multi-Language Business Card OCR Service",
    description=(
        "A production-ready REST API for extracting and parsing business card text. "
        "Supports English and Gujarati OCR, returning structured card data (Email, Website, Location, Owner Name, Company, Designation)."
    ),
    version="1.0.0",
)

# CORS Configuration
# Supports Flutter Web (runs on various localhost ports) and Mobile (runs with file/custom protocols or no origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response Models for Documentation
class OCRData(BaseModel):
    full_name: str = Field("", description="Extracted full name")
    company_name: str = Field("", description="Extracted company name")
    job_title: str = Field("", description="Extracted job title/designation")
    phone_number: List[str] = Field(default_factory=list, description="Extracted phone numbers")
    email: Optional[str] = Field(None, description="Extracted email address")
    website: Optional[str] = Field(None, description="Extracted website URL")
    location: Optional[str] = Field(None, description="Extracted location/address details")
    city: Optional[str] = Field(None, description="Extracted city")
    state: Optional[str] = Field(None, description="Extracted state")
    raw_text: Optional[str] = Field(None, description="Raw extracted text from the card")
    image: Optional[str] = Field(None, description="Image filename")
    id: Optional[int] = Field(None, description="Database record ID")
    user_id: Optional[int] = Field(None, description="User ID")
    updatedAt: Optional[str] = Field(None, description="Updated timestamp")
    createdAt: Optional[str] = Field(None, description="Created timestamp")

class OCRResponse(BaseModel):
    status: str = Field("true", description="Status string ('true' or 'false')")
    message: str = Field("Card scanned and saved successfully", description="Response message")
    data: OCRData = Field(..., description="Card data container")

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Overall system health status")
    tesseract_version: Optional[str] = Field(None, description="Installed Tesseract OCR engine version")
    details: Dict[str, Any] = Field(..., description="Component breakdown details")

# Supported File Types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}

@app.get(
    "/health", 
    response_model=HealthCheckResponse,
    tags=["System Health"],
    summary="Health Check",
    description="Check the health status of the API service and confirm Tesseract is installed and reachable."
)
async def health_check():
    health_status = "healthy"
    tesseract_ver = None
    tesseract_ok = False
    error_detail = None
    
    try:
        tesseract_ver = pytesseract.get_tesseract_version().public
        tesseract_ok = True
    except Exception as e:
        health_status = "unhealthy"
        error_detail = f"Tesseract error: {str(e)}"
        logger.error(f"Health check failed: {error_detail}")

    details = {
        "api": "up",
        "tesseract_reachable": tesseract_ok,
    }
    if error_detail:
        details["error"] = error_detail

    # Return 200 even if unhealthy to let the caller parse the JSON details
    # or return 503 Service Unavailable depending on preferences.
    status_code = status.HTTP_200_OK if health_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    # We construct a response directly
    response = HealthCheckResponse(
        status=health_status,
        tesseract_version=tesseract_ver,
        details=details
    )
    
    return response

@app.post(
    "/extract-text", 
    response_model=OCRResponse,
    tags=["OCR Extraction"],
    summary="Extract and Parse Business Card",
    description="Upload a business card image to run multi-language OCR and extract structured contact fields."
)
async def extract_text(
    file: UploadFile = File(..., description="The business card image file (JPG, JPEG, PNG)"),
    lang: Optional[str] = Query(
        None, 
        description="Override OCR languages. Default is 'eng+guj+hin'. Separate multiple languages with a '+' sign."
    )
):
    # 1. Validate file format
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file.content_type}. Only JPG, JPEG, and PNG images are allowed."
        )

    logger.info(f"Received file upload: '{file.filename}' ({file.content_type})")

    try:
        # 2. Read image content into memory bytes
        file_bytes = await file.read()
        image_stream = io.BytesIO(file_bytes)
        
        # 3. Perform OCR
        raw_text = extract_text_from_image(image_stream, lang=lang)
        
        # 4. Parse the raw text
        parsed_fields = parse_business_card(raw_text)
        
        # Add database structure fields
        parsed_fields.update({
            "image": None,
            "id": None,
            "user_id": None,
            "updatedAt": None,
            "createdAt": None
        })
        
        # 5. Build and return structured response
        return OCRResponse(
            status="true",
            message="Card scanned and saved successfully",
            data=OCRData(**parsed_fields)
        )

    except TesseractNotInstalledError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except LanguagePackMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OCRExtractorError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error in /extract-text endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        await file.close()

if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
