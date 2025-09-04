from typing import Any, Dict, Optional
import os
import json
from pydantic import ValidationError
from dotenv import load_dotenv

from app.models.schemas import ParsedResume, Review, InterviewTopic

# --- LangChain Imports ---
# These replace the direct 'google.genai' imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

# Load environment variables from .env file
load_dotenv()


def analyze_with_gemini(prompt_template_str: str, documents: str, task_type: str = "review") -> Dict[str, Any]:
    """
    Calls the Gemini API using the LangChain framework to analyze documents.
    This is a more robust, maintainable, and extensible approach.
    """
    if not _HAS_LANGCHAIN:
        return {"error": "LangChain libraries not found. Please run 'pip install langchain-google-genai'."}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    try:
        # 1. Initialize the Gemini Chat Model via LangChain
        # We configure it to directly output JSON, which is highly reliable.
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            convert_system_message_to_human=True, # Helps with compatibility
            temperature=0.0, # Lower temperature for more deterministic, structured output
            model_kwargs={"response_mime_type": "application/json"}
        )

        # 2. Define the Prompt Template
        # Note: The 'documents' variable is now an input to the template
        prompt_template = PromptTemplate.from_template(template=prompt_template_str)

        # 3. Define the JSON Output Parser
        # This will automatically parse the model's string output into a Python dict.
        output_parser = JsonOutputParser()

        # 4. Create the "Chain"
        # This links the components: Prompt -> LLM -> Output Parser
        chain = prompt_template | llm | output_parser

        # 5. Invoke the Chain with the input documents
        print(f"Invoking LangChain with model '{model_name}' for task '{task_type}'...")
        # The prompt template expects a variable named 'documents', so we provide it here.
        parsed_response = chain.invoke({"documents": documents})
        
        # 6. Validate the parsed data with Pydantic models
        return _validate_parsed(parsed_response, task_type)

    except Exception as e:
        print(f"An error occurred during the LangChain call: {e}")
        return {"error": "An error occurred while communicating with the Gemini API via LangChain."}


def _validate_parsed(parsed: Dict[str, Any], task_type: str) -> Dict[str, Any]:
    """Validate parsed JSON using Pydantic models according to task_type and normalize output."""
    try:
        if task_type == "review":
            data = parsed.get("review", parsed)
            review_obj = Review(**data)
            return {"review": review_obj.dict()}

        if task_type == "parse_resume":
            data = parsed.get("parsed_resume", parsed)
            resume_obj = ParsedResume(**data)
            return {"parsed_resume": resume_obj.dict()}

        if task_type == "interview":
            items = parsed.get("interviewQuestions", parsed)
            if not isinstance(items, list):
                raise ValueError("Expected a list for interviewQuestions")
            validated = [InterviewTopic(**it).dict() for it in items]
            return {"interviewQuestions": validated}

        return parsed
    except (ValidationError, ValueError) as e:
        return {"error": f"Pydantic validation failed: {str(e)}", "raw_data": parsed}

