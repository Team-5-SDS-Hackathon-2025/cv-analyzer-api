import base64
from typing import Optional

try:
    import fitz  # PyMuPDF
    _HAS_PYMUPDF = True
except ImportError:
    print("WARNING: PyMuPDF (fitz) is not installed. PDF rendering for UI analysis is disabled. Run 'pip install PyMuPDF'.")
    _HAS_PYMUPDF = False


def render_pdf_page_to_base64_image(content: bytes) -> Optional[str]:
    """
    Renders the first page of a PDF into a base64 encoded PNG image string.
    This is used for multimodal analysis of the CV's design and layout.
    
    Args:
        content: The byte content of the PDF file.

    Returns:
        A base64 encoded string of the PNG image, or None if rendering fails.
    """
    if not _HAS_PYMUPDF:
        return None

    try:
        # Open the PDF from the byte content
        with fitz.open(stream=content, filetype="pdf") as doc:
            if not doc:
                return None
            
            # Load the first page
            page = doc.load_page(0)
            
            # Render the page to a pixmap (an image object)
            pix = page.get_pixmap(dpi=150)  # Use a reasonable DPI for quality
            
            # Get the PNG image bytes from the pixmap
            img_bytes = pix.tobytes("png")
            
            # Encode the bytes to a base64 string
            return base64.b64encode(img_bytes).decode('utf-8')
            
    except Exception as e:
        print(f"Error rendering PDF to image: {e}")
        return None
