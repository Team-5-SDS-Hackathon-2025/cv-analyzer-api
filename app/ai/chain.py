from typing import Dict

from app.ai.gemini_client import analyze_with_gemini
from app.ai.prompts import CV_REVIEWER_PROMPT, INTERVIEW_QUESTION_PROMPT, RESUME_PARSER_PROMPT


class ResumeParser:
    """Use AI (Gemini) to convert extracted CV text to structured JSON resume fields."""

    def get_prompt_template(self) -> str:
        # Note the "{documents}" placeholder for LangChain.
        # All literal curly braces in the example output are now escaped with double braces {{ }}.
        return RESUME_PARSER_PROMPT

    def analyze(self, text: str) -> Dict:
        prompt_template = self.get_prompt_template()
        return analyze_with_gemini(prompt_template, text, task_type="parse_resume")



class CVReviewer:
    """Produce a review summary (score, strengths, weaknesses, suggestions)."""

    def get_prompt_template(self) -> str:
        return CV_REVIEWER_PROMPT

    def analyze(self, text: str) -> Dict:
        prompt_template = self.get_prompt_template()
        return analyze_with_gemini(prompt_template, text, task_type="review")


class InterviewQuestionGenerator:
    """Generate interview topics and questions based on the CV."""

    def get_prompt_template(self) -> str:
        return INTERVIEW_QUESTION_PROMPT

    def analyze(self, text: str) -> Dict:
        prompt_template = self.get_prompt_template()
        return analyze_with_gemini(prompt_template, text, task_type="interview")



def analyze_cv_chain(text: str) -> Dict:
    parser = ResumeParser()
    parsed = parser.analyze(text).get("parsed_resume", {})

    reviewer = CVReviewer()
    review = reviewer.analyze(text).get("review", {})

    generator = InterviewQuestionGenerator()
    interview = generator.analyze(text).get("interviewQuestions", [])

    return {"parsed_resume": parsed, "review": review, "interviewQuestions": interview}
