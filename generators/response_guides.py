# generators/response_guides.py

import openai
from prompts.response_guides import get_prompt
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_response_guides(user_input: str, rubric: str) -> str:
    prompt = get_prompt(user_input, rubric)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response guides: {str(e)}"
