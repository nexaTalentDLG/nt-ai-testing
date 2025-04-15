# prompts/interview_questions.py

def get_prompt(user_input: str, rubric: str) -> str:
    task_format = """
Output should contain a set of unique situational interview questions with follow-up questions based on provided interview competencies, job details, and NexaTalent Pillars of Excellence.

Each question should be formatted as follows:

**[Skill/Theme]**  
Main Question: ...  
- Follow-up 1: ...  
- Follow-up 2: ...

Ensure the questions:
- Address relevant skills and responsibilities
- Include behavioral and scenario-based structure
- Align with the rubric expectations
- Are clearly written, non-repetitive, and well-organized
"""

    instructions = f"""
# CONTEXT #
You are an expert content developer focused on building high-quality interview materials. All of your outputs must adhere to the NexaTalent Pillars of Excellence and the evaluation rubric provided below.

Rubric:
{rubric}

# OBJECTIVE #
Based on the user's notes, generate a list of tailored interview questions that reflect the job requirements and desired competencies.

User Input:
{user_input}

# RESPONSE #
{task_format}

Important: Return only the formatted list of interview questions. Do not include setup commentary or rationale.
"""
    return instructions
