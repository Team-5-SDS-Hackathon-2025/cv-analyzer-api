import os
import json
import sys
from fastapi.testclient import TestClient

# Add the project root to the Python path to allow imports from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Initialize the test client for the FastAPI app
client = TestClient(app)


def test_analyze_cv_full_flow():
    """
    Tests the full, end-to-end /api/analyze workflow.
    It uploads a real CV and validates the structure of the comprehensive response.
    """
    # 1. Setup: Define the path to the test CV file
    cv_path = os.path.join("tests", "data", "cv-example-1-1.pdf")
    assert os.path.exists(cv_path), f"Test CV file not found at {cv_path}"

    # 2. Execution: Send the file to the /api/analyze endpoint
    with open(cv_path, "rb") as f:
        files = {"file": (os.path.basename(cv_path), f, "application/pdf")}
        print(f"\nSending file: {os.path.basename(cv_path)} to /api/analyze")
        response = client.post("/api/analyze", files=files)

    # 3. Assertion: Validate the response
    # a) Check for a successful HTTP status code
    assert response.status_code == 200, f"API call failed with status code {response.status_code}: {response.text}"
    
    # b) Parse the JSON response
    data = response.json()
    print("\n--- Full API Response ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-------------------------")

    # c) Validate the top-level structure of the response
    assert isinstance(data, dict), "Response should be a dictionary."
    assert "parsed_resume" in data, "Response must contain the 'parsed_resume' key."
    assert "review" in data, "Response must contain the 'review' key."
    assert "interviewQuestions" in data, "Response must contain the 'interviewQuestions' key."

    # d) Validate the nested structures
    parsed_resume = data["parsed_resume"]
    review = data["review"]
    interview_questions = data["interviewQuestions"]

    assert isinstance(parsed_resume, dict), "'parsed_resume' should be a dictionary."
    assert isinstance(review, dict), "'review' should be a dictionary."
    assert isinstance(interview_questions, list), "'interviewQuestions' should be a list."

    # e) Validate the content of the nested structures
    assert "email" in parsed_resume and parsed_resume["email"], "Parsed resume should contain a non-empty email."
    assert "score" in review and isinstance(review["score"], (int, float)), "Review should contain a numeric score."
    
    print("\nTest passed: The /api/analyze endpoint returned a valid, comprehensive response.")
