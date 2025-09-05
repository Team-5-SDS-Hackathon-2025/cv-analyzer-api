import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Import the initial parsing function
from app.core.extractor import extract_resume_data
# Import the other AI components for the chain
from app.ai.chain import CVDesignReviewer, CVReviewer, InterviewQuestionGenerator
# Import the final, comprehensive response model
from app.core.pdf_renderer import render_pdf_page_to_base64_image
from app.models.schemas import AnalyzeResponse

router = APIRouter()


def _validate_file_type(file: UploadFile) -> None:
    """Helper function to validate the uploaded file's content type."""
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(file: UploadFile = File(...)):
    """
    Receives a CV file, orchestrates the full extraction and chained analysis pipeline,
    and returns a comprehensive result including parsed data, a review, and interview questions.
    """
    _validate_file_type(file)
    content = await file.read()

    # --- Pre-process file for both text and image analysis ---
    base64_image = None
    if file.filename.lower().endswith(".pdf"):
        print("Rendering PDF to image for design analysis...")
        base64_image = render_pdf_page_to_base64_image(content)

    # --- Step 1: Parse the CV ---
    # This calls the two-step process: unstructured -> Gemini parser
    print("Step 1: Parsing resume...")
    parser_result = extract_resume_data(content=content, filename=file.filename)

    # Validate the crucial first step
    if not parser_result or "parsed_resume" not in parser_result:
        error_detail = parser_result.get("error", "An unknown error occurred during parsing.")
        raise HTTPException(status_code=500, detail=error_detail)
    
    parsed_resume = parser_result["parsed_resume"]
    print("Step 1: Success.")

    # Convert the parsed resume dict back into a clean JSON string for the next AI steps
    structured_resume_json = json.dumps(parsed_resume, indent=2, ensure_ascii=False)

    # --- Step 2: Review the Parsed Data ---
    print("Step 2: Reviewing parsed data...")
    design_review = {}
    if base64_image:
        print("Step 4: Analyzing CV design from image...")
        design_reviewer = CVDesignReviewer()
        design_review_result = design_reviewer.analyze(base64_image)
        design_review = design_review_result.get("design_review", {})
        
    reviewer = CVReviewer()
    review_result = reviewer.analyze(structured_resume_json)
    review = review_result.get("review", {})
    print("Step 2: Success.")

    # --- Step 3: Generate Interview Questions from Parsed Data ---
    print("Step 3: Generating interview questions...")
    generator = InterviewQuestionGenerator()
    interview_result = generator.analyze(structured_resume_json)
    interview_questions = interview_result.get("interviewQuestions", [])
    print("Step 3: Success.")

    # --- Step 4: Combine and Return ---
    final_result = {
        "parsed_resume": parsed_resume,
        "design_review": design_review,
        "review": review,
        "interviewQuestions": interview_questions
    }
    
    return JSONResponse(content=final_result)

