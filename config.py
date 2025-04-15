# config.py

import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ASSISTANT_IDS = {
    "Write a job description": "asst_1TJ2x5bhc1n4mS9YhOVcOFaJ",
    "Build Interview Questions": "asst_6jdd2oSBhocieeiDvQxnUNJ4",
    "Create response guides": "asst_B5g1JWvRl0Mr0Bl9lHKcQums",
    "Evaluate candidate responses": "asst_JI8Xr4zWgmsh6h2F5XF3aBkZ"
}

SPINNER_TEXTS = {
    "Write a job description": "Drafting your job description...",
    "Build Interview Questions": "Building your interview questions...",
    "Create response guides": "Creating your response guides...",
    "Evaluate candidate responses": "Evaluating your candidate's responses..."
}

MAIN_LOGGER_URL = "https://script.google.com/macros/s/AKfycbwzjOx4zpLDZw3qaSjEiXHA7XsMgUsWmOwpjC3R4kFoQ5o6RNUNXk886K1LyNZSFxl1/exec"
WARNING_LOGGER_URL = "https://script.google.com/macros/s/AKfycbwzjOx4zpLDZw3qaSjEiXHA7XsMgUsWmOwpjC3R4kFoQ5o6RNUNXk886K1LyNZSFxl1/exec"
CONSENT_TRACKER_URL = "https://script.google.com/macros/s/AKfycbxyGOLTYLV53dpevb1dsTuG0UVmq9twvcy45FK7SIgt3DFhW5uuKL4TQTNr4tT5ckMN/exec"

RUBRIC_FILENAMES = {
    "Write a job description": "NexaTalent Rubric for Job Description Evaluation.txt",
    "Build Interview Questions": "NexaTalent Rubric for Interview Question Generation.txt",
    "Create response guides": "NexaTalent Rubric for Candidate Responses.txt",
    "Evaluate candidate responses": "NexaTalent Rubric for Candidate Responses.txt"
}

TASK_OVERVIEWS = {
    "Write a job description": "Create a job description that is clear, role-aligned, and matches NexaTalent's standards.",
    "Build Interview Questions": "Develop structured behavioral and situational interview questions tailored to the role.",
    "Create response guides": "Generate example answers across all rubric levels to help interviewers calibrate expectations.",
    "Evaluate candidate responses": "Analyze a candidate’s response using NexaTalent’s rubric and provide structured scoring and feedback."
}

TASK_LOOK_FORS = {
    "Write a job description": (
        "Assume the user is trying to create a job description. Inputs are considered aligned if they describe a role’s purpose, expectations, or context. "
        "Only flag the submission if it clearly lacks any role-specific information, appears completely off-topic, or includes inappropriate or malicious content. "
        "\n\nIdeal submissions include details about the job title, responsibilities, qualifications, or work environment, and may mention the company or desired tone."
    ),
    "Build Interview Questions": (
        "Assume the user wants to generate job-specific interview questions. Valid inputs often include a job description, required skills, or relevant competencies. "
        "Only flag submissions that are clearly unrelated to hiring or appear to be attempting to access generalized AI advice or capabilities. "
        "\n\nIdeal submissions describe the role, mention behavioral traits or core responsibilities, or include desired focus areas such as scenario-based questions."
    ),
    "Create response guides": (
        "Assume the user wants example answers to interview questions. Inputs are considered aligned if they contain interview prompts or question-like content. "
        "Only flag the submission if there is no interview context or if the content appears off-topic or focused on generic AI output. "
        "\n\nIdeal submissions include one or more clearly stated interview questions or follow-ups, potentially grouped by skill or domain."
    ),
    "Evaluate candidate responses": (
        "Assume the user is submitting a candidate’s response for evaluation. Inputs are valid if they include an answer to an interview question, even if informally formatted. "
        "Only flag if the input contains no response content or appears to request general AI analysis rather than candidate-specific scoring. "
        "\n\nIdeal submissions include the interview question(s) and the candidate’s response. Follow-ups, if present, provide valuable structure for assessment."
    )
}
