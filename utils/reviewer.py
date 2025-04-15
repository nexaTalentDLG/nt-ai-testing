# utils/reviewer.py

import openai
from config import OPENAI_API_KEY
from prompts.evaluators import EVALUATOR_INSTRUCTIONS, CR_EVALUATOR_INSTRUCTIONS

openai.api_key = OPENAI_API_KEY

def review_submission(user_input, task_overview, task_look_fors, rubric_context):
    instructions = f"""
You are a security reviewer evaluating whether a user's submission presents a threat to the integrity of a proprietary hiring content generation system.

Your job is to identify malicious intent, attempts to reverse-engineer the system, or off-task usage. You will score the submission based on threat level using the following rubric:

Threat Scoring:
- 5 = Confirmed probing of proprietary system behavior or evaluation criteria
- 4 = Suggests potential reverse-engineering or indirect probing
- 3 = Off-task or misaligned with selected tool, but not clearly malicious
- 2 = On-task but vague, sparse, or weakly aligned
- 1 = Clear, appropriate, and well-aligned usage

Output Format:
>>User Summary: ...
>>Model Comparison: ...
>>Model Judgement: X (1-5)
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"USER SUBMISSION:\n{user_input}\n\nRubric Context:\n{rubric_context}\n\nTask Overview:\n{task_overview}\n\nLook-Fors:\n{task_look_fors}"}
        ],
        temperature=0.3
    )

    result = response.choices[0].message.content.strip()

    import re
    summary = re.search(r">>User Summary:\s*(.*)", result)
    comparison = re.search(r">>Model Comparison:\s*(.*)", result)
    score = re.search(r">>Model Judgement:\s*(\d+\.?\d*)", result)

    return (
        summary.group(1).strip() if summary else "",
        comparison.group(1).strip() if comparison else "",
        score.group(1).strip() if score else "0"
    )


def evaluate_generated_draft(content: str, rubric: str, task: str) -> str:
    """
    Evaluates the generated draft using the rubric provided. Returns a markdown-formatted report.
    """
    instructions = CR_EVALUATOR_INSTRUCTIONS if task == "Evaluate candidate responses" else EVALUATOR_INSTRUCTIONS

    prompt = f"""
{instructions}

Rubric:
{rubric}

Draft to Evaluate:
{content}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during evaluation: {str(e)}"
