from io import BytesIO
import os
from typing import Dict, Optional

from app.ai.chain import ResumeParser

# --- PDF Processing with PyMuPDF ---
try:
    import fitz  # PyMuPDF
    _HAS_PYMUPDF = True
except ImportError:
    print("WARNING: PyMuPDF (fitz) is not installed. PDF processing will be less reliable. Run 'pip install PyMuPDF'.")
    _HAS_PYMUPDF = False

# --- DOCX Processing with python-docx ---
try:
    from docx import Document
    _HAS_DOCX = True
except ImportError:
    print("WARNING: python-docx is not installed. DOCX file support is disabled. Run 'pip install python-docx'.")
    _HAS_DOCX = False


# --- OCR Processing ---
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    _HAS_OCR = True
except ImportError:
    print("WARNING: OCR dependencies missing. Run 'pip install pytesseract pdf2image pillow'.")
    _HAS_OCR = False


def extract_text_from_file(filename: str, content: bytes) -> str:
    """
    Extracts text from a CV file.
    - PDF → PyMuPDF, fallback to OCR if scanned
    - DOCX → python-docx
    - Others → fallback decode
    """
    file_ext = filename.lower().split('.')[-1]
    print(f"Processing file: {filename}, Detected extension: {file_ext}")

    # --- PDF Extraction Logic ---
    if file_ext == "pdf" and _HAS_PYMUPDF:
        print("Processing PDF with PyMuPDF...")
        try:
            with fitz.open(stream=content, filetype="pdf") as doc:
                pages_text = [page.get_text("text").strip() for page in doc]
                full_text = "\n".join(pages_text).strip()

                if full_text:
                    return full_text
                else:
                    print("Warning: PDF extracted but text is empty. Trying OCR...")

                    # --- OCR Fallback ---
                    if _HAS_OCR:
                        images = convert_from_bytes(content)
                        ocr_text = []
                        for i, img in enumerate(images):
                            page_text = pytesseract.image_to_string(img)
                            ocr_text.append(page_text.strip())
                        return "\n".join(ocr_text).strip()
                    else:
                        print("OCR not available. Cannot process scanned PDF.")
        except Exception as e:
            print(f"Error processing PDF with PyMuPDF: {e}")

    # --- DOCX Extraction Logic ---
    if file_ext == "docx" and _HAS_DOCX:
        print("Processing DOCX with python-docx...")
        try:
            doc = Document(BytesIO(content))
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            if paragraphs:
                return "\n".join(paragraphs)
            else:
                print("Warning: DOCX extracted but no text found.")
        except Exception as e:
            print(f"Error processing DOCX with python-docx: {e}")

    # --- Fallback for other file types or failed extractions ---
    print("Using fallback text decoder...")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        print("UTF-8 decoding failed. Falling back to latin-1.")
        return content.decode("latin-1", errors="ignore")
        print("UTF-8 decoding failed. Falling back to latin-1.")
        return content.decode("latin-1", errors="ignore")



def extract_resume_data(content: bytes, filename: str) -> Dict:
    """
    Orchestrates the new, more reliable resume data extraction process.
    """
    # Step 1: Extract a layout-aware, structured JSON from the file.
    structured_json_str = extract_text_from_file(filename, content)

    if not structured_json_str:
        return {"error": "Failed to extract structured data using unstructured."}

    # Step 2: Use the AI-powered parser to convert the structured JSON into the final, semantic JSON.
    parser = ResumeParser()
    parsed_data = parser.analyze(structured_json_str)
    print(f"Extracted data: {parsed_data}")

    return parsed_data
