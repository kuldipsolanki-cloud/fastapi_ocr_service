# Multi-Language Business Card OCR & Parsing Service

This is a production-ready, self-contained Python FastAPI backend service designed to perform OCR on business cards and parse the unstructured text output into structured JSON fields. It supports English and Gujarati, extraction of emails, websites, phone numbers, owner names, company names, designation titles, and address locations.

---

## Project Structure

```
fastapi_ocr_service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application instance, routes, CORS & Swagger
│   ├── config.py        # Configuration and path settings for Tesseract
│   ├── ocr.py           # Image pre-processing & PyTesseract extraction
│   ├── parser.py        # Rule-based regex & heuristic card parser
│   └── utils.py         # Standard logging setup
├── flutter_example/
│   └── ocr_uploader.dart # Complete cross-platform Flutter upload client widget
├── requirements.txt     # Python dependencies
└── README.md            # Detailed instructions (this file)
```

---

## Tesseract OCR Engine Installation

Tesseract OCR is a system library and must be installed separately from the Python environment.

### 1. Windows Installation
1. Download the latest Windows installer from **UB Mannheim**:
   - [Tesseract OCR Windows Installers](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer:
   - **Crucial step for Gujarati support**: During installation, under the "Additional script data" or "Additional language data" options, scroll down and check **Gujarati** (or select all languages). This automatically installs `guj.traineddata`.
   - Complete the installation. By default, it installs to `C:\Program Files\Tesseract-OCR\`.
3. **Configure PATH Environment Variable**:
   - Press the Windows Key and search for **"Edit the system environment variables"**.
   - Click the **"Environment Variables..."** button.
   - Under **System variables**, select **Path** and click **Edit...**.
   - Click **New** and add: `C:\Program Files\Tesseract-OCR`
   - Click **OK** on all windows to save.
4. Restart your terminal/IDE for PATH modifications to take effect.

*Note: If Tesseract is installed to the default directory, `app/config.py` will find it automatically, even if you did not add it to the system Path.*

### 2. Linux (Ubuntu / Debian) Installation
1. Update packages and install Tesseract:
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```
2. Install the Gujarati language pack:
   ```bash
   sudo apt-get install tesseract-ocr-guj
   ```

### 3. macOS Installation
1. Install via Homebrew:
   ```bash
   brew install tesseract
   ```
2. Download Gujarati language pack (`guj.traineddata`):
   - Download the file from the [Official Tesseract Tessdata Repository](https://github.com/tesseract-ocr/tessdata/blob/main/guj.traineddata).
   - Move it to your Homebrew tessdata directory:
     - **Apple Silicon M1/M2/M3**: `/opt/homebrew/share/tessdata/`
     - **Intel Macs**: `/usr/local/share/tessdata/`

---

## FastAPI Backend Setup & Running

This project requires **Python 3.11+**.

### 1. Set Up Virtual Environment
Navigate to the project directory:
```bash
cd fastapi_ocr_service
```

Create a virtual environment:
- **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Service
Start the FastAPI server:
```bash
python app/main.py
```
Or use Uvicorn command:
```bash
uvicorn app.main:app --reload
```

The service will be live at: `http://localhost:8000`
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Verification & API Usage Examples

### 1. Health Check Endpoint
Verify that the service is running and Tesseract is correctly found:
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "tesseract_version": "5.3.4",
  "details": {
    "api": "up",
    "tesseract_reachable": true
  }
}
```

### 2. OCR Text Extraction Endpoint (`/extract-text`)
Send an image file using `curl`:
- **Windows PowerShell**:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/extract-text" -Method Post -Form @{ file = Get-Item "C:\path\to\your\business_card.png" }
  ```
- **Bash (Linux/macOS)**:
  ```bash
  curl -X POST "http://localhost:8000/extract-text" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/path/to/your/business_card.png"
  ```

**Expected Response Schema**:
```json
{
  "success": true,
  "text": "ABC Tech Ltd\nRajesh Patel\nManaging Director\nPhone: +91 9876543210\nEmail: rajesh@abctech.com\nWebsite: www.abctech.com\nLocation: 101, Shanti Tower, SG Highway, Ahmedabad, Gujarat - 380054\nસંચાલક",
  "parsed_data": {
    "owner_name": "Rajesh Patel",
    "designation": "Managing Director",
    "company_name": "ABC Tech Ltd",
    "email": "rajesh@abctech.com",
    "website": "www.abctech.com",
    "location": "101, Shanti Tower, SG Highway, Ahmedabad, Gujarat - 380054",
    "phones": [
      "+91 98765 43210"
    ]
  }
}
```

---

## Python Integration Code
You can also run a quick verification script in Python:

```python
import requests

url = "http://localhost:8000/extract-text"
image_path = "path/to/card.jpg"

with open(image_path, "rb") as f:
    files = {"file": (image_path, f, "image/jpeg")}
    # Optional: override language, e.g., 'eng' for English only or 'guj' for Gujarati only
    # params = {"lang": "eng"}
    response = requests.post(url, files=files)
    
print(response.json())
```

---

## Docker Quickstart (For Node.js / Other Backend Developers)

This project includes a `Dockerfile` that packages Python, Tesseract, and Gujarati language data automatically. The backend developer doesn't need to install Python or Tesseract on their system to run it.

### 1. Build the Docker Image
```bash
docker build -t fastapi-ocr-service .
```

### 2. Run the Container
```bash
docker run -d -p 8000:8000 fastapi-ocr-service
```
Once run, the service will be live on `http://localhost:8000`.

---

## Node.js Integration Example (Axios)

The Node.js developer can call this service from their Express/NestJS/Node backend using `axios` and `form-data`:

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Function to call the FastAPI OCR Service
async function parseBusinessCard(imagePath) {
  const form = new FormData();
  // Read the uploaded image from Node.js file system
  form.append('file', fs.createReadStream(imagePath));

  try {
    const response = await axios.post('http://localhost:8000/extract-text', form, {
      headers: {
        ...form.getHeaders(),
      },
    });

    if (response.data.success) {
      const parsedData = response.data.parsed_data;
      console.log('Parsed Card Details:', parsedData);
      
      // Access structured fields:
      console.log('Name:', parsedData.owner_name);
      console.log('Company:', parsedData.company_name);
      console.log('Designation:', parsedData.designation);
      console.log('Email:', parsedData.email);
      console.log('Website:', parsedData.website);
      console.log('Location:', parsedData.location);
      console.log('Phones:', parsedData.phones);
    }
  } catch (error) {
    console.error('OCR API Error:', error.response ? error.response.data : error.message);
  }
}

// Example usage:
// parseBusinessCard('./path/to/card.jpg');
```

