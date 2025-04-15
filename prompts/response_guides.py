# prompts/response_guides.py

def get_prompt(user_input: str, rubric: str) -> str:
    task_format = """
For each question, generate five sample responses that align with levels 1 through 5 of the NexaTalent rubric:
- **Concern**
- **Mild Concern**
- **Mixed**
- **Mild Strength**
- **Strength**

Each response should:
- Be clear, realistic, and appropriate for the question
- Reflect the proficiency level's tone and content depth
- Be labeled correctly and grouped per question

At the end, include a summary table comparing the five levels.
"""

    instructions = f"""
# CONTEXT #
You are a response generation assistant helping create realistic candidate examples for interviewer training.

Rubric:
{rubric}

# OBJECTIVE #
Given user-submitted questions or context, generate a response guide across five rubric levels. Ensure each sample is useful for comparison training.

User Input:
{user_input}

# RESPONSE #
{task_format}

Important: Only return the formatted responses. Do not include analysis or setup commentary.
"""
    return instructions
