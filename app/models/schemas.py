from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Review(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class QuestionItem(BaseModel):
    question: str
    difficulty: str


class InterviewTopic(BaseModel):
    topic: str
    topic_en: str
    questions: List[QuestionItem]


class WorkExperienceItem(BaseModel):
    company: str = ""
    position: str = ""
    duration: str = ""
    role_description: str = ""


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    time_of_project: str = ""


class AwardItem(BaseModel):
    name: str = ""

class CertificationItem(BaseModel):
    name: str = ""

class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: List[str] = []
    work_experience: List[WorkExperienceItem] = []
    projects: List[ProjectItem] = []
    education: List[Dict[str, Any]] = []
    certifications: List[CertificationItem] = []
    awards: List[AwardItem] = []
    languages: List[str] = []
    location: str = ""


class AnalyzeResponse(BaseModel):
    review: Review
    interviewQuestions: List[InterviewTopic]
    parsed_resume: ParsedResume

