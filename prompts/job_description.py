# prompts/job_description.py

def get_prompt(user_input: str, rubric: str) -> str:
    task_format = """
Output should contain the following headings: "About Us, Job Summary, Key Responsibilities, Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment". 
Each section should build upon the previous ones to create a cohesive narrative. Use bullet points for Responsibilities, Requirements, and Benefits sections. 
Keep the About Us section under 150 words. Ensure all requirements listed are truly mandatory, including location and citizenship requirements when applicable. 
Always verify salary ranges comply with local pay transparency laws and reference specific technologies/tools rather than general terms whenever possible.
Ensure that your final output is evaluated against the quality standards provided in the rubric context above.
"""

    instructions = f"""
# CONTEXT #
You are a highly skilled assistant specializing in creating high-quality hiring materials. All of your outputs must adhere to the NexaTalent Pillars of Excellence and be evaluated against the rubric provided in the context below:

Rubric:
{rubric}

# OBJECTIVE #
Craft a professional, clear, and well-structured job description based on the user's submission below.

User Input:
{user_input}

# RESPONSE #
{task_format}

Important: Only provide the final job description output. Do not include reasoning, analysis, or commentary.
"""
    return instructions
