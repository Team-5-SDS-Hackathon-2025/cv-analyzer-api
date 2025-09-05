from typing import Dict, Optional

# Import the new multimodal client function and the new prompt
from app.ai.gemini_client import analyze_with_gemini, analyze_with_gemini_multimodal
from app.ai.prompts import CV_REVIEWER_PROMPT, INTERVIEW_QUESTION_PROMPT, RESUME_PARSER_PROMPT, DESIGN_REVIEWER_PROMPT


class ResumeParser:
    """Use AI (Gemini) to convert extracted CV text to structured JSON resume fields."""

    def analyze(self, text: str) -> Dict:
        # Use the prompt template string directly
        return analyze_with_gemini(RESUME_PARSER_PROMPT, text, task_type="parse_resume")


class CVReviewer:
    """Produce a review summary (score, strengths, weaknesses, suggestions) from text."""

    def analyze(self, text: str) -> Dict:
        return analyze_with_gemini(CV_REVIEWER_PROMPT, text, task_type="review")


class InterviewQuestionGenerator:
    """Generate interview topics and questions based on the CV text."""

    def analyze(self, text: str) -> Dict:
        return analyze_with_gemini(INTERVIEW_QUESTION_PROMPT, text, task_type="interview")


# --- New Class for Design Review ---
class CVDesignReviewer:
    """Analyzes the visual design of a CV from an image."""

    def analyze(self, base64_image: str) -> Dict:
        """
        Analyzes the CV's design using a multimodal AI call.

        Args:
            base64_image: A base64 encoded string of the CV's image.

        Returns:
            A dictionary containing the structured design review.
        """
        # This calls a new, specialized function in the gemini_client that handles images.
        return analyze_with_gemini_multimodal(DESIGN_REVIEWER_PROMPT, base64_image, task_type="design_review")


# --- Updated Orchestration Function ---
def analyze_cv_chain(text: str, base64_image: Optional[str] = None) -> Dict:
    """
    Orchestrates the full analysis pipeline, now including an optional design review.
    """
    parser = ResumeParser()
    parsed_result = parser.analyze(text)
    parsed_resume = parsed_result.get("parsed_resume", {})

    reviewer = CVReviewer()
    review_result = reviewer.analyze(text)
    review = review_result.get("review", {})

    generator = InterviewQuestionGenerator()
    interview_result = generator.analyze(text)
    interview_questions = interview_result.get("interviewQuestions", [])

    # --- New Design Review Step ---
    design_review = {}
    if base64_image:
        print("Step 4: Analyzing CV design from image...")
        design_reviewer = CVDesignReviewer()
        design_review_result = design_reviewer.analyze(base64_image)
        design_review = design_review_result.get("design_review", {})
        print("Step 4: Success.")
    
    return {
        "parsed_resume": parsed_resume,
        "review": review,
        "interviewQuestions": interview_questions,
        "design_review": design_review
    }

