import os
import openai
import streamlit as st
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

openai.api_key = api_key

###############################################################################
# Mappings for dynamic assistant IDs
###############################################################################
ASSISTANT_IDS = {
    "Write a job description": "asst_1TJ2x5bhc1n4mS9YhOVcOFaJ",
    "Build Interview Questions": "asst_6jdd2oSBhocieeiDvQxnUNJ4",
    "Create response guides": "asst_B5g1JWvRl0Mr0Bl9lHKcQums",
    "Evaluate candidate responses": "asst_JI8Xr4zWgmsh6h2F5XF3aBkZ"
}

###############################################################################
# Mappings for dynamic spinner text
###############################################################################
SPINNER_TEXTS = {
    "Write a job description": "Drafting your job description...",
    "Build Interview Questions": "Building your interview questions...",
    "Create response guides": "Creating your response guides...",
    "Evaluate candidate responses": "Evaluating your candidate's responses..."
}

###############################################################################
# Helper Functions for Input Analysis and Validation
###############################################################################
import re

def summarize_input(user_input):
    # Generate a brief summary of the user's input
    summary = "Summary of input: " + re.sub(r'\s+', ' ', user_input[:250])  # Use the first 250 chars
    return summary

def validate_task_alignment(task, input_summary):
    """
    Compares the user input summary to the task and determines if they align.
    Returns:
        - is_aligned (bool): Whether the task and input align.
        - justification (str): Explanation of why or why not.
    """
    if task.lower() in input_summary.lower():
        return True, f"The user's input aligns with the selected task '{task}'."
    else:
        return False, f"The user's input does not align with the selected task '{task}'. Please review the input and try again."


###############################################################################
# Confidentiality Message
###############################################################################
CONFIDENTIALITY_MESSAGE = """
It looks like you may be trying to complete a task that this tool hasn’t yet been fine-tuned to handle. At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.

To maintain these standards, we’ve designed this app with a specific focus, ensuring it delivers high-quality, reliable results through a carefully crafted process.

If you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com.
"""


###############################################################################
# MASTER_INSTRUCTIONS: Full instructions with placeholders [TASK] and [task_format]
###############################################################################
MASTER_INSTRUCTIONS = """
# CONTEXT #
You are a helpful assistant that aids hiring teams in the creation of hiring materials and supports. 
Everything you create uses the NexaTalent Pillars of Excellence as a foundation for building quality content. 
You have NexaTalent Rubrics as a part of your knowledge base which you use to improve the quality of your work. 

# OBJECTIVE #
When a user submits content to you, follow the following steps:

1. Before generating content, analyze the submitted input and generate a summary of what it is the user is attempting to do. == {user_summary}
    ***NOTE: Rememeber the user is likely asking to complete a task that will help them with hiring. Consider this in the generation of {user_summary}
2. Review your task,[TASK], and generate a summary of what this means you should be trying to do for the user. == {model_summary}
3. Compare {user_summary} and {model_summary} to determine how similar these tasks are. Give me a brief summary of how similar these tasks are. This summary == {model_comparison}
4. Use {model_comparison} to generate a similarity score between 0 and 5 where 0 is completely different tasks and 5 is the exact same. This score should be a numeric value and be set to the variable {model_judgement}
    ***NOTE: Be sure to consider different ways [TASK] might be phrased when making this judgement. For example asking to "create" or expressing a "need" for 
    interview questions would be the same as asking to "build" interview questions. 
4. If {model_judgement} has a value less than or equal to 2, respond with the confidentiality message below:
   "[confidentiality_message]"
5. If {model_judgement} has a value greater than 2, proceed to review any additional content submitted by the user 
   and create an initial draft of the final output.
6. Knowing that you are being asked to help [TASK], review the Pillars of Excellence along with the detailed breakdowns of each pillar and create a summary of how these documents will help you ensure a quality output. 
7. Review any additional content submitted by the user and create an initial draft of the final output.
***NOTE: Consider the [task_format] when generating your initial draft
8. Use the rubric in your knowledge base to check the quality of your output, and write a summary of how you would score your initial draft.
9. Make any adjustments as needed to improve the quality of the output for your final draft. 

# STYLE #
You are an expert in the generation of hiring content with experience in writing job descriptions, 
creating interview questions, generating sample responses to help interviewers evaluate candidates, 
and grading candidate responses to interview questions. You leverage samples and resources from your 
knowledge base and reference them frequently throughout the content generation process to ensure the 
quality of your outputs is always at the highest level. 

# TONE #
Your tone should be educational and informative. Outputs should be concise and use language that is free of jargon or overly expressive.

# AUDIENCE #
Hiring team members and hiring managers

# RESPONSE #
>>{user_summary}
>>{model_summary}
>>{model_comparison}
>>{model_judgement}
[task_format]
"""

###############################################################################
# TASK_FORMAT_DEFINITIONS: Full text for each [task_format] based on selection
###############################################################################
TASK_FORMAT_DEFINITIONS = {
    "Write a job description": """
Output should contain the following headings: “About Us, Job Summary, Key Responsibilities, Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment”. 
Each section should build upon the previous ones to create a cohesive narrative. Use bullet points for Responsibilities, Requirements, and Benefits sections. 
Keep About Us section under 150 words. Ensure all requirements listed are truly mandatory. Include location and citizenship requirements when applicable. 
Always verify salary ranges comply with local pay transparency laws. Reference specific technologies/tools rather than general terms when possible. Follow the initial example below for the formatting of each section:

EXAMPLE:
**About Us**
At Intuitive Safety Solutions, we are dedicated to providing top-tier safety consulting services, helping our clients create safer workplaces across industries. Our commitment to excellence, innovation in safety solutions, and a workplace culture that values diversity, equity, and inclusion are at the heart of everything we do.

**Job Summary**
We are seeking a local Senior Safety Manager to join us as an Owner's Representative on a project in the Folsom, California area. The project will encompass the construction of a new lab and improvements to existing tenant spaces. This pivotal role will steer our on-site safety initiatives, ensuring a safe and compliant work environment for all project participants.

**Key Responsibilities**
- Lead the implementation of comprehensive safety protocols for the construction project.
- Conduct regular safety inspections and audits to identify and mitigate risks.
- Act as a key liaison between the project team, contractors, and stakeholders on matters related to safety.
- Develop and deliver safety training sessions to project staff and contractors.
- Manage incident investigation processes, including reporting and follow-up actions to prevent recurrence.
- Continuously update safety documentation and compliance records in alignment with local, state, and federal regulations.

>>>Continue this formatting for the Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment sections following the instructions above.

""",
    "Build Interview Questions": """
Output should contain a set of unique situational interview questions with follow up questions based on provided interview competencies, 
information provided, and NexaTalent Pillars of Excellence. Each question should be formatted as follows:

EXAMPLE:
>>User Summary: The user is seeking to create interview questions for a mid-level Nurse position at Care Partners in Omaha, NE. They have provided detailed information about the organization, job summary, key responsibilities, requirements, qualifications, key skills, benefits, salary, and work environment to guide the development of relevant interview questions that align with the competencies needed for the role.
>>Model Summary: The task of building interview questions involves creating a set of situational questions that assess candidates' competencies, experiences, and qualifications relevant to the mid-level Nurse position. These questions should be tailored to reflect the responsibilities and skills outlined in the job description and should help interviewers evaluate the suitability of candidates for the role.
>>Model Judgement: The tasks of the user and the model are highly similar, as both involve the creation of interview questions specifically designed for the Nurse position. The focus is on assessing the candidates' abilities and experiences related to the provided job details. Thus, I would score this a 5.
 
**Experience with Club Channel Sales**
Main Question: Can you describe a successful initiative you’ve led in the Club Channel space that delivered significant business growth? What was your role, and how did you measure success?
- Follow-up 1: How did you address challenges during this initiative, especially regarding broker partner management?
- Follow-up 2: What strategies did you use to ensure alignment across cross-functional teams?

""",
    "Create response guides": """
Output should contain a set of sample responses based on NexaTalent rubric in your knowledge base. 
For each question you should write 5 sample responses that align with levels 1 through 5 in the NexaTalent rubric. 
These will be labeled concern, mild-concern, mixed, mild-strength, or strength respectively in your final output. 
You should generate one set of samples for each Main Question set, considering follow-up questions as part of the sample responses.

**Main Question**
Can you explain your approach to creating a strategic sales plan that aligns with an organization’s goals?

**Concern** 
- The candidate is unable to articulate a clear or comprehensive planning approach.
**Mild Concern**
- The candidate gives a basic outline without showing how it aligns with organizational goals, suggesting limited strategic insight.
**Mixed** 
- The candidate provides some alignment strategies but lacks depth in describing how they integrate these into the sales plan.
**Mild Strength** 
- The candidate outlines a clear plan with alignment strategies, showing an understanding of goal integration.
**Strength** 
- The candidate articulates a detailed strategic plan that aligns with goals and provides examples of successful execution.

""",
    "Evaluate candidate responses": """
Output should be a numerical score between 1-5 grading the candidates overall performance. This should be followed with a justification paragraph. 
There will also be a score of 1-5 for each individual question with justifications for the scoring.
For scoring you will use the NexaTalent Rubric for Candidate Evaluation to assess and grade responses.
For justification paragraphs you will cite examples from the candidates response and connect them to the rubric as appropriate.
"""
}

###############################################################################
# Streamlit UI
###############################################################################
st.title("NexaTalent AI")
st.subheader("Your assistant for generating high-quality hiring content.")

# User selects a task
task = st.selectbox(
    "Select a task:",
    [
        "Write a job description",
        "Build Interview Questions",
        "Create response guides",
        "Evaluate candidate responses"
    ]
)

# User selects input method
input_method = st.radio(
    "How would you like to provide additional notes or information?",
    ("Paste text", "Upload file")
)

user_notes = ""
if input_method == "Paste text":
    user_notes = st.text_area("Enter additional notes or information:")
else:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md", "rtf", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
            user_notes = string_data.read()

###############################################################################
# Generate Button
###############################################################################
if st.button("Generate"):
    if not user_notes.strip():
        st.warning("Please provide text or upload a file with valid content.")
    else:
        # Dynamically select assistant ID and spinner text
        assistant_id = ASSISTANT_IDS[task]
        spinner_text = SPINNER_TEXTS[task]

        with st.spinner(spinner_text):
            chosen_task_format = TASK_FORMAT_DEFINITIONS[task]
            final_instructions = (
                MASTER_INSTRUCTIONS
                .replace("[TASK]", task)
                .replace("[task_format]", chosen_task_format.strip())
                .replace("[confidentiality_message]", CONFIDENTIALITY_MESSAGE)
                + "\n\n"
                "# ADDITIONAL NOTE #\n"
                "Only provide the final output per the #RESPONSE# section. "
                "Do not include any chain-of-thought, steps, or internal reasoning."
            )

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": f"USER NOTES:\n{user_notes}"}
                    ],
                    temperature=0.7
                )

                # Extract the generated response
                final_response = response.choices[0].message.content.strip()

                # Parse {model_judgement} value from the response
                model_judgement_value = None
                if "{model_judgement}" in final_response:
                    try:
                        judgement_line = final_response.split("{model_judgement}")[1].split("\n")[0].strip()
                        model_judgement_value = int(judgement_line)  # Convert to an integer
                    except ValueError:
                        st.error("Unable to parse {model_judgement} value as an integer.")
                        st.stop()

                # Check if {model_judgement} is less than or equal to 2
                if model_judgement_value is not None and model_judgement_value <= 2:
                    st.warning(CONFIDENTIALITY_MESSAGE)
                else:
                    # Strip everything before the first relevant header for valid content
                    if "**" in final_response:
                        clean_output = final_response.split("**", 1)[1]
                        clean_output = "**" + clean_output  # Re-add the header
                    else:
                        clean_output = final_response  # Fallback to the full response if no header is found

                    # Display the cleaned content
                    st.text_area("Generated Content", value=clean_output.strip(), height=400)

            except Exception as e:
                st.error(f"An error occurred: {e}")
