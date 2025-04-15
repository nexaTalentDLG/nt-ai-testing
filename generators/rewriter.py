# generators/rewriter.py

import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def revise_draft_with_feedback(draft: str, evaluation: str, rubric: str, task: str) -> str:
    """
    Refines the assistant-generated draft using feedback from an evaluator and the rubric.
    Returns a polished, final version.
    """
    instructions = f"""
You are a content rewriting assistant.

Your task is to revise the following draft based on:
- The evaluator's feedback
- The rubric expectations

Maintain the original intent, but improve clarity, alignment, tone, and formatting.
Only return the final version — do not include commentary or markdown.

Task: {task}

Rubric:
{rubric}

Evaluator Feedback:
{evaluation}

Original Draft:
{draft}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": draft}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during refinement: {str(e)}"