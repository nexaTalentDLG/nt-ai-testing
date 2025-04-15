# prompts/candidate_eval.py

def get_prompt(user_input: str, rubric: str) -> str:
    task_format = """
Output should be a numerical score between 1-5 grading the candidate's overall performance. This should be followed by a justification paragraph.
Also include scores and justifications for each individual question (main and follow-ups).

Format:
**Overall Score: X**  
[Justification]

**Main Question Score: X**  
[Justification]

**Follow-up 1 Score: X**  
[Justification]

**Follow-up 2 Score: X**  
[Justification]

All analysis must reference the rubric.
"""

    instructions = f"""
# CONTEXT #
You are evaluating a candidate's response to structured interview questions using the NexaTalent rubric.

Rubric:
{rubric}

# OBJECTIVE #
Based on the user's submission, score and justify performance across all parts of the response.

User Input:
{user_input}

# RESPONSE #
{task_format}

Important: Return only the formatted score + justifications. No commentary or repetition of rubric details.
"""
    return instructions
