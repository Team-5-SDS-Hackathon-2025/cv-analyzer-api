from typing import Dict

from app.ai.gemini_client import analyze_with_gemini


class ResumeParser:
    """Use AI (Gemini) to convert extracted CV text to structured JSON resume fields."""

    def get_prompt_template(self) -> str:
        # Note the "{documents}" placeholder for LangChain.
        # All literal curly braces in the example output are now escaped with double braces {{ }}.
        return (
            'CONTEXT: You are a resume parsing AI. Your task is to convert unstructured CV text into a structured JSON object.\n\n'
            'QUERY: Carefully analyze the provided CV text and extract the following fields:\n'
            '- name: The full name of the candidate.\n'
            '- email: The primary email address.\n'
            '- phone: The primary phone number.\n'
            '- summary: A brief professional summary.\n'
            '- skills: A list of key professional, technical, and soft skills.\n'
            '- work_experience: A list of professional employment roles. Each item must be a formal job with a specific company, position/role, and employment duration. Do not include personal projects here.\n'
            '- projects: A list of personal or academic projects, each with "name", "description", "team_size", and "time_of_project (if any))".\n'
            '- education: A list of educational qualifications, each with "degree", "institution", and "year".\n'
            '- certifications: A list of relevant certifications.\n'
            '- languages: A list of languages spoken.\n'
            '- location: The candidate\'s general location (e.g., "Hanoi, Vietnam").\n\n'
            'Return a single JSON object with the key "parsed_resume". The value should be an object containing the extracted fields. '
            'Ensure all field types match the specified schema. If a field is not found, use an appropriate empty value (e.g., "" for strings, [] for lists).\n\n'
            'INPUT: The extracted CV text is below.\n'
            '```text\n'
            '{documents}\n'
            '```\n\n'
            'OUTPUT FORMAT: Return only the JSON object, with no additional commentary.\n\n'
            'EXAMPLE OUTPUT:\n'
            '{{\n'
            '    "parsed_resume": {{\n'
            '        "name": "John Doe",\n'
            '        "email": "john.doe@example.com",\n'
            '        "phone": "+1 555-123-4567",\n'
            '        "summary": "Senior backend engineer with 6 years of experience building APIs in Python.",\n'
            '        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],\n'
            '        "work_experience": [\n'
            '            {{"company": "Microsoft", "position": "Senior Backend Engineer", "duration": "2019-2024"}}\n'
            '        ],\n'
            '        "projects": [\n'
            '            {{"name": "CV Analysis API", "description": "Developed a FastAPI backend to parse resumes.", "team_size": 1, "time_of_project": "Q1 2024"}}\n'
            '        ],\n'
            '        "education": [\n'
            '            {{"degree": "BSc Computer Science", "institution": "State University", "year": "2017"}}\n'
            '        ],\n'
            '        "certifications": ["AWS Certified Developer"],\n'
            '        "languages": ["English", "Spanish"],\n'
            '        "location": "Hanoi, Vietnam"\n'
            '    }}\n'
            '}}\n'
        )

    def analyze(self, text: str) -> Dict:
        prompt_template = self.get_prompt_template()
        return analyze_with_gemini(prompt_template, text, task_type="parse_resume")



class CVReviewer:
    """Produce a review summary (score, strengths, weaknesses, suggestions)."""

    def get_prompt_template(self) -> str:
        return (
            'CONTEXT: You are an expert hiring manager and career coach in the candidate\'s field. Your task is to evaluate a CV and provide a structured JSON review.\n\n'
            'INSTRUCTIONS: Analyze the candidate\'s professional profile. Provide an overall score from 1-10 based on clarity, impact, and experience. List specific, actionable items for the following fields:\n'
            '- strengths: Identify clear, compelling positive aspects. Focus on quantifiable achievements, relevant experience, and strong skillsets.\n'
            '- weaknesses: Pinpoint areas for improvement. Note any lack of detail, missing key skills, or unclear career progression.\n'
            '- suggestions: Offer concrete, actionable advice for the candidate to improve their CV. For example, "Quantify project impact with metrics."\n\n'
            'INPUT: The extracted CV text is below.\n'
            '```text\n'
            '{documents}\n'
            '```\n\n'
            'OUTPUT FORMAT: Return only the JSON object, with no additional commentary.\n\n'
            'EXAMPLE OUTPUT:\n'
            '{{\n'
            '    "review": {{\n'
            '        "score": 8.5,\n'
            '        "strengths": ["Strong Java & Spring Boot experience shown in projects.", "Good understanding of microservices concepts like Kafka."],\n'
            '        "weaknesses": ["\'Individual Projects\' lack real-world team collaboration context.", "Project durations in the future (e.g., \'January 2025\') are confusing."],\n'
            '        "suggestions": ["Clarify project timelines. Rephrase \'Individual Project\' to highlight the technologies learned and problems solved."]\n'
            '    }}\n'
            '}}\n'
        )

    def analyze(self, text: str) -> Dict:
        prompt_template = self.get_prompt_template()
        return analyze_with_gemini(prompt_template, text, task_type="review")


class InterviewQuestionGenerator:
    """Generate interview topics and questions based on the CV."""

    def get_prompt_template(self) -> str:
        return (
            'CONTEXT: You are a senior professional and expert interviewer in the candidate\'s field. Your task is to generate insightful interview questions based on the candidate\'s CV.\n\n'
            'INSTRUCTIONS: Create questions that directly probe the experience and skills listed in the CV. Group them by topic and assign a difficulty.\n\n'
            'INPUT: The extracted CV text is below.\n'
            '```text\n'
            '{documents}\n'
            '```\n\n'
            'OUTPUT FORMAT: Return only the JSON object, with no additional commentary.\n\n'
            'EXAMPLE OUTPUT:\n'
            '{{\n'
            '    "interviewQuestions": [\n'
            '        {{\n'
            '            "topic": "Java & Spring Boot Experience",\n'
            '            "topic_en": "java_spring_boot_experience",\n'
            '            "questions": [\n'
            '                {{"question": "In your \'Business Directory API\' project, what was the most challenging Spring Boot feature you implemented and why?", "difficulty": "medium"}},\n'
            '                {{"question": "You list Kafka as a skill. How would you integrate Kafka into a Spring Boot microservice to handle asynchronous tasks?", "difficulty": "hard"}}\n'
            '            ]\n'
            '        }},\n'
            '        {{\n'
            '            "topic": "Problem Solving",\n'
            '            "topic_en": "problem_solving",\n'
            '            "questions": [\n'
            '                {{"question": "Describe the algorithm you used for your \'File Compressor\' project. What were its time and space complexities?", "difficulty": "hard"}}\n'
            '            ]\n'
            '        }}\n'
            '    ]\n'
            '}}\n'
        )

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
