import json
import os
import tempfile
from typing import Optional, Dict, List, Any

from app.ai.chain import ResumeParser

try:
    # Use the generic auto partition which detects file type
    from unstructured.partition.auto import partition
    _HAS_UNSTRUCTURED = True
except ImportError:
    _HAS_UNSTRUCTURED = False


def extract_structured_json_from_file(filename: str, content: bytes) -> Optional[str]:
    """
    Extracts structured content from a CV file using the 'unstructured' library
    and returns it as a JSON formatted string.

    This is the crucial first step that preserves the document's layout and context.
    """
    if not _HAS_UNSTRUCTURED:
        print("Warning: 'unstructured' library not found. Parsing will be unreliable.")
        try:
            raw_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = content.decode("latin-1", errors="ignore")
        fallback_data = [{"type": "RawText", "text": raw_text}]
        return json.dumps(fallback_data, indent=2, ensure_ascii=False)

    path = None
    try:
        suffix = f".{filename.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            path = tmp.name

        elements = partition(filename=path)
        structured_data: List[Dict[str, Any]] = [
            {"type": el.__class__.__name__, "text": str(el)} for el in elements
        ]
        return json.dumps(structured_data, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error partitioning file with unstructured: {e}")
        return None
    finally:
        if path and os.path.exists(path):
            os.unlink(path)


def extract_resume_data(content: bytes, filename: str) -> Dict:
    """
    Orchestrates the new, more reliable resume data extraction process.
    """
    # Step 1: Extract a layout-aware, structured JSON from the file.
    structured_json_str = extract_structured_json_from_file(filename, content)

    if not structured_json_str:
        return {"error": "Failed to extract structured data using unstructured."}

    # Step 2: Use the AI-powered parser to convert the structured JSON into the final, semantic JSON.
    parser = ResumeParser()
    parsed_data = parser.analyze(structured_json_str)
    print(f"Extracted data: {parsed_data}")

    return parsed_data
