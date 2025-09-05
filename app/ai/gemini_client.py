from typing import Any, Dict, Optional
import os
import json
from pydantic import ValidationError
from dotenv import load_dotenv

from app.models.schemas import ParsedResume, Review, InterviewTopic, DesignReview

# --- LangChain Imports ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    # Import for handling multimodal messages
    from langchain_core.messages import HumanMessage
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

# Load environment variables from .env file
load_dotenv()


def _safe_json_parse(s: str) -> Optional[Dict[str, Any]]:
    """Try to robustly parse JSON from a string. Try direct loads first, then extract first JSON object substring."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = s[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return None
        return None


def analyze_with_gemini(prompt_template_str: str, documents: str, task_type: str = "review") -> Dict[str, Any]:
    """
    Calls the Gemini API using the LangChain framework to analyze TEXT documents.
    """
    if not _HAS_LANGCHAIN:
        return {"error": "LangChain libraries not found. Please run 'pip install langchain-google-genai'."}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0,
            model_kwargs={"response_mime_type": "application/json"}
        )
        prompt_template = PromptTemplate.from_template(template=prompt_template_str)
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser

        print(f"Invoking LangChain with model '{model_name}' for task '{task_type}'...")
        parsed_response = chain.invoke({"documents": documents})
        
        return _validate_parsed(parsed_response, task_type)

    except Exception as e:
        print(f"An error occurred during the LangChain call: {e}")
        return {"error": "An error occurred while communicating with the Gemini API via LangChain."}


def analyze_with_gemini_multimodal(prompt_template_str: str, base64_image: str, task_type: str = "design_review") -> Dict[str, Any]:
    """
    Calls the Gemini API using LangChain with both a text prompt and an image for multimodal analysis.
    """
    if not _HAS_LANGCHAIN:
        return {"error": "LangChain libraries not found."}
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set."}

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

    try:
        # Initialize the model, which can handle multimodal inputs
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0,
            model_kwargs={"response_mime_type": "application/json"}
        )

        # Create a message structure that includes both the text prompt and the image data
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_template_str},
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64_image}"
                }
            ]
        )
        
        output_parser = JsonOutputParser()
        chain = llm | output_parser
        
        print(f"Invoking LangChain Multimodal for task '{task_type}'...")
        parsed_response = chain.invoke([message])
        
        return _validate_parsed(parsed_response, task_type)

    except Exception as e:
        print(f"An error occurred during the LangChain multimodal call: {e}")
        return {"error": "An error occurred during multimodal analysis."}


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

        if task_type == "design_review":
            data = parsed.get("design_review", parsed)
            design_obj = DesignReview(**data)
            return {"design_review": design_obj.dict()}

        return parsed
    except (ValidationError, ValueError) as e:
        print(f"Pydantic validation failed for task '{task_type}': {str(e)}")
        return {"error": f"Pydantic validation failed: {str(e)}", "raw_data": parsed}

