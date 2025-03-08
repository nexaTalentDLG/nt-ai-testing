import os
import openai
import streamlit as st
import requests
import json
from io import StringIO
from dotenv import load_dotenv
import re
from datetime import datetime
from zoneinfo import ZoneInfo  # For timezone support
import tiktoken

# Add this after imports but before any other Streamlit commands
st.set_page_config(
    page_title="NexaTalent AI",
    page_icon="reference_materials/NT Icon.png",
    layout="centered"
)

# Load environment variables
load_dotenv()

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

openai.api_key = api_key

###############################################################################
# Helper function for token counting
###############################################################################

def count_tokens(text):
    """Count tokens using tiktoken, OpenAI's tokenizer"""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")  # or whatever model you're using
    return len(encoding.encode(text))

def compute_tokens_for_stage(system_msg, user_msg):
    """Compute tokens for system and user messages using tiktoken"""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")  # or whatever model you're using
    return {
        "system": len(encoding.encode(system_msg)),
        "user": len(encoding.encode(user_msg))
    }

###############################################################################
# Helper function for timestamp in PST with 12-hour format
###############################################################################
def get_current_timestamp():
    # Returns timestamp in PST (America/Los_Angeles) in 12-hour format with AM/PM
    return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m/%d/%Y %I:%M:%S %p")

###############################################################################
# Consent Tracker Setup (Updated webhook)
###############################################################################
CONSENT_TRACKER_URL = "https://script.google.com/macros/s/AKfycbxyGOLTYLV53dpevb1dsTuG0UVmq9twvcy45FK7SIgt3DFhW5uuKL4TQTNr4tT5ckMN/exec"

def log_consent(email):
    """
    Logs the timestamp, email address, and consent status ("I agree")
    to a Google Form via the provided webhook.
    """
    timestamp = get_current_timestamp()
    data = {
        "timestamp": timestamp,
        "email": email,
        "consent": "I agree",
        "ip_address": ""
    }
    try:
        response = requests.post(CONSENT_TRACKER_URL, json=data)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to log consent. Status code: {response.status_code}")  # Log to console
            return None
    except Exception as e:
        print(f"Consent logging error: {str(e)}")  # Log to console
        return None

# Ensure consent is tracked in session state.
if "consent" not in st.session_state:
    st.session_state.consent = False

# Display consent UI if consent is not yet given.
if not st.session_state.consent:
    consent_container = st.empty()  # Create a container for the consent UI.
    with consent_container.container():
        st.markdown("## NexaTalent Consent Agreement")
        st.write('This version of the NexaTalent app is currently in a testing phase. By entering your email and pressing **I understand and accept** you agree to the following:')

        # Generate today's date in PST in a readable format.
        today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y")
        user_agreement_text = f"""EARLY QUALITATIVE TESTING AGREEMENT & MUTUAL NON-DISCLOSURE AGREEMENT
Effective Date: {today}
Parties: This agreement is between NexaTalent ("Provider") and the individual accepting these terms ("Tester").
This Agreement sets forth the terms under which the Tester is granted access to NexaTalent's pre-alpha product for qualitative testing while ensuring confidentiality and proper handling of proprietary information.

SECTION 1: EARLY QUALITATIVE TESTING AGREEMENT
This section governs the Tester's participation in NexaTalent's pre-alpha testing phase, where feedback will be collected to refine product usability, functionality, and experience.
1. Confidentiality
   The Tester acknowledges that all materials, discussions, prototypes, designs, test data, feedback, documentation, and any related information provided before, during, or after the testing phase are confidential and proprietary to NexaTalent.
   Tester agrees not to share, copy, disclose, or distribute any information related to the Testing Session, including but not limited to screenshots, descriptions, recordings, discussions, or findings.
   Any and all insights, feedback, reports, or analysis generated during testing become the exclusive intellectual property of NexaTalent.
   These confidentiality obligations remain in effect for three (3) years from the date of acceptance or until NexaTalent publicly releases the Product, whichever is later.
   Any breach of confidentiality may result in immediate termination of this Agreement and legal action as permitted by law.
2. Scope of Testing
   The Tester agrees to evaluate the Product using NexaTalent's designated platforms (e.g., Streamlit app, Google Sheets, email feedback forms). Testing includes:
   - Completing assigned tasks as instructed.
   - Logging and documenting identified issues.
   - Providing structured feedback via feedback forms, discussions, or debrief sessions.
3. Data Handling & Privacy
   NexaTalent is committed to responsible data management and Tester privacy:
   - Tester feedback will be anonymized before being included in reports or presentations.
   - Personal information required for testing will be minimized and stored securely.
   - While NexaTalent takes reasonable precautions to protect data, the company is not liable for unintended data breaches or cybersecurity incidents.
4. No Compensation
   The Tester acknowledges that participation is voluntary and that they will not receive financial compensation for any activities related to the Testing Session, including past, current, or future testing engagements.
5. Limitations of Liability
   The Product is provided "as is" and may contain bugs, incomplete features, or unexpected performance issues.
   NexaTalent is not responsible for any damage to the Tester's device, loss of data, or other issues resulting from participation in testing.
   NexaTalent, its employees, officers, and affiliates are not liable for any damages resulting from unforeseen data breaches or technical failures.
6. Termination
   Either party may terminate this Agreement with written notice.
   Upon termination, the Tester must return or destroy all confidential materials related to the Product as directed by NexaTalent.
   Even after termination, the Tester remains bound by the three (3)-year confidentiality obligation outlined in Section 1.
7. Dispute Resolution
   Any disputes arising under this Agreement will be resolved through binding arbitration in Washington State under the rules of the American Arbitration Association.
   Both parties waive any rights to litigate in court, except to enforce arbitration awards or seek injunctive relief.

SECTION 2: MUTUAL NON-DISCLOSURE AGREEMENT
This section ensures that confidential and proprietary information shared between NexaTalent and the Tester remains protected and undisclosed to third parties.
1. Definition of Confidential Information
   "Confidential Information" includes, but is not limited to:
   - Business, financial, customer, product, and service details.
   - Intellectual property, trade secrets, inventions, and methodologies.
   - Any documentation, schematics, prototypes, test results, or discussions related to NexaTalent's operations or products.
   - Any third-party confidential information provided by NexaTalent.
2. Exclusions from Confidential Information
   Confidential Information does not include information that:
   - Becomes publicly available without violation of this Agreement.
   - Is legally obtained from a third party without confidentiality obligations.
   - Was already known by the Tester prior to disclosure, as evidenced by written records.
   - Is independently developed by the Tester without using NexaTalent's confidential information.
3. Tester Obligations
   The Tester agrees to:
   - Maintain strict confidentiality regarding all disclosed information.
   - Use the information solely for testing purposes and not for any personal, competitive, or commercial advantage.
   - Not disclose, share, or distribute any confidential materials to third parties without NexaTalent's prior written consent.
4. Required Disclosure by Law
   If legally compelled to disclose confidential information, the Tester must:
   - Provide prompt written notice to NexaTalent.
   - Limit disclosure to only the portion required by law.
5. Return or Destruction of Confidential Information
   Upon termination of this Agreement, or at NexaTalent's request, the Tester must:
   - Return or permanently delete all confidential information in their possession.
   - Provide written certification confirming destruction of all copies.
6. Term & Survival
   This Agreement remains in effect for three (3) years from the date of acceptance.
   Confidentiality obligations related to trade secrets continue indefinitely.
7. Governing Law & Dispute Resolution
   This Agreement is governed by the laws of Washington State.
   Any disputes will be resolved through binding arbitration in Seattle, WA under the American Arbitration Association.

ACKNOWLEDGMENT & ACCEPTANCE
By clicking "I understand and accept", you acknowledge that:
 ✅ You have read, understood, and agree to the Early Qualitative Testing Agreement and the Mutual Non-DDisclosure Agreement.
 ✅ You accept all terms, including confidentiality, liability limitations, and dispute resolution.
 ✅ You understand that NexaTalent reserves the right to enforce this Agreement, including through legal means if necessary.
"""
        st.text_area("User Agreement", value=user_agreement_text, height=200, disabled=True)
        st.write('Please enter a valid email. This is used for communicating updates and providing support.')

        # Email input field.
        email = st.text_input("Enter your email address:")
        
        # Button is disabled until an email is entered.
        if st.button("I understand and accept", disabled=(not re.match(r"[^@]+@[^@]+\.[^@]+", email))):
            if log_consent(email) is not None:
                st.session_state.consent = True
                consent_container.empty()
    
    if not st.session_state.consent:
        st.stop()

###############################################################################
# Warning Logger
###############################################################################
WARNING_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwzjOx4zpLDZw3qaSjEiXHA7XsMgUsWmOwpjC3R4kFoQ5o6RNUNXk886K1LyNZSFxl1/exec"

def log_warning_to_google_sheets(
    tool_selection,
    user_input,
    initial_submitted_tokens=None,
    initial_instructions_tokens=None,
    initial_prompt_tokens=None,
    initial_output_tokens=None,
    user_summary=None,
    model_comparison=None,
    model_judgement=None
):
    """
    Logs warning data to the WarningLog sheet when a submission doesn't match the task.
    """
    timestamp = get_current_timestamp()
    data = {
        "log_type": "warning",  # This tells our Apps Script to use the warning logger
        "timestamp": timestamp,
        "tool_selection": tool_selection,
        "user_input": user_input,
        "initial_submitted_tokens": initial_submitted_tokens if initial_submitted_tokens is not None else "",
        "initial_instructions_tokens": initial_instructions_tokens if initial_instructions_tokens is not None else "",
        "initial_prompt_tokens": initial_prompt_tokens if initial_prompt_tokens is not None else "",
        "initial_completion_tokens": initial_output_tokens if initial_output_tokens is not None else "",
        "user_summary": user_summary if user_summary is not None else "",
        "model_comparison": model_comparison if model_comparison is not None else "",
        "model_judgement": model_judgement if model_judgement is not None else ""
    }
    try:
        response = requests.post(WARNING_WEBHOOK_URL, json=data)
        return response.text
    except Exception as e:
        return f"Warning logging error: {e}"

###############################################################################
# Updated Logging Function with New WebApp URL (Main Logger)
###############################################################################
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwzjOx4zpLDZw3qaSjEiXHA7XsMgUsWmOwpjC3R4kFoQ5o6RNUNXk886K1LyNZSFxl1/exec"

def log_to_google_sheets(
    tool_selection,
    user_input,
    initial_output,
    evaluator_feedback,
    evaluator_score,
    refined_output,
    # API usage token metrics:
    initial_prompt_tokens=None,
    initial_completion_tokens=None,
    evaluator_prompt_tokens=None,
    evaluator_completion_tokens=None,
    final_prompt_tokens=None,
    final_completion_tokens=None,
    overall_total_tokens=None,
    # New separate token metrics:
    initial_instructions_tokens=None,
    initial_submitted_tokens=None,
    evaluator_instructions_tokens=None,
    evaluator_submitted_tokens=None,
    final_instructions_tokens=None,
    final_submitted_tokens=None,
    feedback=None,
    user_summary=None,
    model_comparison=None,
    model_judgement=None
):
    """
    Sends log data including the generated outputs, API usage token metrics, and
    the new separate token tracking fields to the specified Google Sheet via the provided webhook.
    """
    timestamp = get_current_timestamp()
    data = {
        "timestamp": timestamp,
        "tool_selection": tool_selection,
        "user_input": user_input,
        "initial_output": initial_output,
        "evaluator_feedback": evaluator_feedback,
        "evaluator_score": evaluator_score,
        "refined_output": refined_output,
        "initial_prompt_tokens": initial_prompt_tokens if initial_prompt_tokens is not None else "",
        "initial_completion_tokens": initial_completion_tokens if initial_completion_tokens is not None else "",
        "evaluator_prompt_tokens": evaluator_prompt_tokens if evaluator_prompt_tokens is not None else "",
        "evaluator_completion_tokens": evaluator_completion_tokens if evaluator_completion_tokens is not None else "",
        "final_prompt_tokens": final_prompt_tokens if final_prompt_tokens is not None else "",
        "final_completion_tokens": final_completion_tokens if final_completion_tokens is not None else "",
        "overall_total_tokens": overall_total_tokens if overall_total_tokens is not None else "",
        "initial_instructions_tokens": initial_instructions_tokens if initial_instructions_tokens is not None else "",
        "initial_submitted_tokens": initial_submitted_tokens if initial_submitted_tokens is not None else "",
        "evaluator_instructions_tokens": evaluator_instructions_tokens if evaluator_instructions_tokens is not None else "",
        "evaluator_submitted_tokens": evaluator_submitted_tokens if evaluator_submitted_tokens is not None else "",
        "final_instructions_tokens": final_instructions_tokens if final_instructions_tokens is not None else "",
        "final_submitted_tokens": final_submitted_tokens if final_submitted_tokens is not None else "",
        "feedback": feedback if feedback is not None else "",
        "user_summary": user_summary if user_summary is not None else "",
        "model_comparison": model_comparison if model_comparison is not None else "",
        "model_judgement": model_judgement if model_judgement is not None else ""
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.text
    except Exception as e:
        return f"Logging error: {e}"


###############################################################################
# Evaluator Function
###############################################################################

def evaluate_content(generated_output, rubric_context):
    """
    Sends the generated output and rubric context to the evaluator assistant (OpenAI)
    and returns the evaluation feedback and score, along with token usage.
    """
    try:
        # Create a thread for the evaluation
        thread = openai.beta.threads.create()
        
        # Add the evaluation request message to the thread
        message_content = (
            f"{EVALUATOR_INSTRUCTIONS}\n\n"
            f"Rubric Context:\n{rubric_context}\n\n"
            f"Content to Evaluate:\n{generated_output}\n\n"
        )
        
        # Create message and track approximate token usage
        message = openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
        
        # Run the assistant on the thread
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_YVQKg7useHzYPRWMYb3HY7o6"
        )
        
        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            run = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        # Get the assistant's response
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        evaluator_text = messages.data[0].content[0].text.value.strip()
        
        # Approximate token counts for logging
        evaluator_prompt_tokens = count_tokens(message_content)
        evaluator_completion_tokens = count_tokens(evaluator_text)
        evaluator_total_tokens = evaluator_prompt_tokens + evaluator_completion_tokens
        
        # Extract the score - updated to handle decimal values
        score_match = re.search(r"Score:\s*(\d+\.?\d*)", evaluator_text)
        score = float(score_match.group(1)) if score_match else None
        
        if score is None:
            print("Could not extract score from evaluator response")  # Log to console
            
        return (score, evaluator_text, 
                evaluator_prompt_tokens, evaluator_completion_tokens, evaluator_total_tokens)
        
    except Exception as e:
        print(f"Evaluator error: {str(e)}")  # Log to console
        return None, "", 0, 0, 0

###############################################################################
# Review Function
###############################################################################
def review_submission(user_input, task_overview, task_look_fors, rubric_context):
    """
    Reviews the user's submission to confirm it aligns with the selected task.
    Follows steps 1-6 in the Master instructions and outputs:
      user_summary, model_comparison, and model_judgement.
    """
    review_instructions = (
        "Please review the following user's submission for alignment with the selected task.\n"
        "1. Review the user's submission along with the provided rubric context.\n"
        "2. Identify all relevant details from the submission as outlined: " + task_look_fors + "\n"
        "3. Generate a concise summary of what the user is asking for. == {user_summary}\n"
        "4. Analyze the task overview: " + task_overview + " and summarize what your output should accomplish.\n"
        "5. Compare the user summary and the task overview to determine task similarity. Provide a comparison summary == {model_comparison}\n"
        "6. Based on the comparison, output a similarity score between 0 and 5 (0 means entirely different; 5 means identical). This numeric score should be set as {model_judgement}\n\n"
        "Output your response exactly in the following format:\n"
        ">>User Summary: <your user summary here>\n"
        ">>Model Comparison: <your model comparison here>\n"
        ">>Model Judgement: <your model judgement here>\n"
    )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": review_instructions},
            {"role": "user", "content": f"USER SUBMISSION:\n{user_input}\n\nRubric Context:\n{rubric_context}"}
        ],
        temperature=0.7
    )
    review_output = response.choices[0].message.content.strip()
    
    # Extract the variables using regular expressions.
    user_summary_match = re.search(r">>User Summary:\s*(.*)", review_output)
    model_comparison_match = re.search(r">>Model Comparison:\s*(.*)", review_output)
    model_judgement_match = re.search(r">>Model Judgement:\s*(.*)", review_output)
    
    user_summary = user_summary_match.group(1).strip() if user_summary_match else ""
    model_comparison = model_comparison_match.group(1).strip() if model_comparison_match else ""
    model_judgement = model_judgement_match.group(1).strip() if model_judgement_match else "0"
    
    return user_summary, model_comparison, model_judgement


###############################################################################
# Extract Model 
###############################################################################

def extract_evaluation_parts(text):
    """
    Extracts user_summary, model_comparison, and model_judgement from the given text.
    Improved to handle more variations and be more robust.
    """
    # Define multiple patterns to match different possible formats
    user_summary_patterns = [
        r">>User Summary:\s*(.*?)(?=>>|\Z)",  # Standard format with >> prefix
        r"User Summary:\s*(.*?)(?=Model|User|\Z)",  # Without >> prefix
        r"user_summary\s*=\s*['\"](.*?)['\"]",  # Variable assignment format
        r"\{user_summary\}:\s*(.*?)(?=\{|\Z)"  # Template format
    ]
    
    model_comparison_patterns = [
        r">>Model Comparison:\s*(.*?)(?=>>|\Z)",
        r"Model Comparison:\s*(.*?)(?=Model|User|\Z)",
        r"model_comparison\s*=\s*['\"](.*?)['\"]",
        r"\{model_comparison\}:\s*(.*?)(?=\{|\Z)"
    ]
    
    model_judgement_patterns = [
        r">>Model Judgement:\s*(\d+\.?\d*)",  # Match numeric values with >> prefix
        r"Model Judgement:\s*(\d+\.?\d*)",    # Without >> prefix
        r"model_judgement\s*=\s*['\"]?(\d+\.?\d*)['\"]?",  # Variable assignment
        r"\{model_judgement\}:\s*(\d+\.?\d*)"  # Template format
    ]
    
    # Function to try multiple patterns and return the first match
    def try_patterns(patterns, default=""):
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                return match.group(1).strip()
        return default
    
    user_summary = try_patterns(user_summary_patterns)
    model_comparison = try_patterns(model_comparison_patterns)
    model_judgement = try_patterns(model_judgement_patterns, "0")
    
    return user_summary, model_comparison, model_judgement

def ensure_logging_values(
    user_summary, 
    model_comparison, 
    model_judgement, 
    fallback_user_summary="", 
    fallback_model_comparison="", 
    fallback_model_judgement="0"
):
    """
    Ensures that the logging values are valid and not empty.
    Returns sanitized values for logging.
    """
    # Ensure user_summary is a non-empty string
    if not user_summary or not isinstance(user_summary, str) or not user_summary.strip():
        user_summary = fallback_user_summary or "Not available"
    
    # Ensure model_comparison is a non-empty string
    if not model_comparison or not isinstance(model_comparison, str) or not model_comparison.strip():
        model_comparison = fallback_model_comparison or "Not available"
    
    # Ensure model_judgement is a valid number (as string)
    try:
        # Try to convert to float and back to string to validate
        float_judgement = float(model_judgement)
        model_judgement = str(float_judgement)
    except (ValueError, TypeError):
        model_judgement = fallback_model_judgement or "0"
    
    return user_summary, model_comparison, model_judgement


def extract_actionable_feedback(evaluator_text):
    """
    Extracts the actionable feedback summary from the evaluator's response.
    """
    # Try multiple possible section headers
    patterns = [
        r"## Actionable Feedback\s*(.*?)(?=##|$)",
        r"Actionable Feedback[:\s]*(.*?)(?=##|$)",
        r"## Final Summary\s*(.*?)(?=##|$)",
        r"Final Summary[:\s]*(.*?)(?=##|$)",
    ]
    
    for pattern in patterns:
        summary_match = re.search(pattern, evaluator_text, re.DOTALL | re.IGNORECASE)
        if summary_match and summary_match.group(1).strip():
            return summary_match.group(1).strip()
    
    # If no match found, try to extract any content after the last score
    last_score_pattern = r"Score:\s*\d+\.?\d*\s*(.*?)$"
    last_score_match = re.search(last_score_pattern, evaluator_text, re.DOTALL)
    if last_score_match and last_score_match.group(1).strip():
        return last_score_match.group(1).strip()
    
    return "No actionable feedback found"

###############################################################################
# Mappings and Helper Texts
###############################################################################
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

TASK_LOOK_FORS = {
    "Write a job description": (
        "Users may submit information about job details, such as job title, responsibilities, qualifications, location, pay range, "
        "and details about the company. Look for specific job requirements or preferences that need to be incorporated."
    ),
    "Build Interview Questions": (
        "Users may submit a job description, competencies, or specific areas they want interview questions to focus on. "
        "They might also ask for questions related to specific skills or experiences relevant to the role."
    ),
    "Create response guides": (
        "Users may submit a question or set of questions for which they need example responses. "
        "They might also ask for help understanding how to evaluate responses using the NexaTalent rubric."
    ),
    "Evaluate candidate responses": (
        "Users may submit responses from candidates or summaries of candidate answers. "
        "Look for specific examples of candidate behavior or statements that need to be evaluated."
    )
}

TASK_OVERVIEWS = {
    "Write a job description": (
        "This task involves crafting a detailed job description that includes sections like 'About Us', 'Job Summary', "
        "'Key Responsibilities', 'Requirements', 'Qualifications', and more. The goal is to attract qualified candidates "
        "by clearly defining the role, responsibilities, and expectations."
    ),
    "Build Interview Questions": (
        "This task focuses on creating a set of unique situational interview questions tailored to the job's competencies "
        "and requirements. These questions are designed to assess a candidate's suitability for the role, using follow-up "
        "questions to explore their experience and problem-solving skills."
    ),
    "Create response guides": (
        "This task requires generating sample responses for the interview questions using the NexaTalent rubric. "
        "Each response corresponds to proficiency levels (e.g., Concern, Mixed, Strength) and helps interviewers "
        "evaluate candidates' answers effectively."
    ),
    "Evaluate candidate responses": (
        "This task involves analyzing and scoring candidates' responses to interview questions using a 1-5 scale. "
        "Justifications for the scores are provided, citing examples from the responses and linking them to the NexaTalent rubric."
    )
}

###############################################################################
# Evaluation Instructions
###############################################################################
EVALUATOR_INSTRUCTIONS = """
## Your Role
You are an expert evaluator tasked with assessing candidate responses based on specific rubric dimensions. You will receive evaluation rubrics dynamically and must apply them accurately and consistently to evaluate content.

## General Evaluation Process

1. **Understand the Rubric**
   - Carefully read and internalize the provided rubric
   - Note the dimension name, key components, and rationale
   - Understand the level descriptions (typically 1-5) and their distinguishing characteristics

2. **Analyze the Content**
   - Read the candidate's response thoroughly
   - Identify specific evidence related to the rubric dimension
   - Look for both explicit statements and implicit demonstrations of the skills being evaluated

3. **Match Evidence to Level Criteria**
   - Compare the identified evidence against each level's description and attributes
   - Determine which level best matches the overall quality of the response
   - Consider both strengths and weaknesses in the candidate's response

4. **Provide a Structured Evaluation**
   - Assign a specific level (1-5)
   - Justify your rating with concrete evidence from the response
   - Offer constructive feedback for improvement when appropriate

## Evaluation Framework

For each evaluation, structure your assessment as follows:

### 1. Dimension Summary
- Briefly restate the dimension being evaluated
- Note the key components being assessed

### 2. Evidence Analysis
- Identify 2-3 specific examples from the response that relate to the dimension
- For each example, explain how it demonstrates skills relevant to the rubric
- Note both strengths and areas for development

### 3. Level Assignment
- Assign a specific level (1-5)
- Provide a clear justification for why this level was chosen over others
- Reference specific attributes from the rubric level description that match the response

### 4. Feedback Summary
- Offer 1-2 constructive suggestions for improvement (for levels 1-4)
- Highlight specific strengths to maintain (for all levels)
- Frame feedback in terms of specific actions the candidate could take

## Evaluation Principles

- **Evidence-Based**: Ground all assessments in specific evidence from the response
- **Balanced**: Consider both strengths and areas for development
- **Consistent**: Apply the same standards across all evaluations
- **Specific**: Avoid vague generalizations; provide concrete examples
- **Constructive**: Frame feedback to enable improvement

## Actionable Feedback

After reviewing all dimensions and completing the steps above. Create a final summary of the feedback with acitonable steps for the main model to improve its response.

## Important Considerations

- Focus on the specific dimension being evaluated, even if the response contains elements relevant to other dimensions
- Maintain objectivity and avoid bias in your evaluations
- Consider the response holistically while still providing specific evidence
- Apply the rubric as written without adding additional criteria
- When in doubt between two levels, review the specific attributes of each level and select the one with more matching characteristics
- Use the NexaTalent 9 Pillars of Excellence from your knowledge base as a foundation of values as you complete this work

IMPORTANT: Always start your response with 'Score: X' where X is your numerical score (0-5) that averages the scores from all 5 dimensions.
"""

###############################################################################
# MASTER_INSTRUCTIONS
###############################################################################
MASTER_INSTRUCTIONS = """
# CONTEXT #
You are a highly skilled assistant specializing in creating high-quality hiring materials. All of your outputs must adhere to the NexaTalent Pillars of Excellence and be evaluated against the rubric provided in the context above. Use the rubric as the standard for quality and for grading your output.

# OBJECTIVE #
When you receive a submission that is not feedback, do the following:
1. Review the rubric above to ensure you understand how to produce a quality output.
2. Review the user's submission along with the rubric context provided.
3. Identify all relevant details from the submission (e.g., job details, required competencies, or candidate responses) as outlined in [TASK_LOOK_FORS].
4. Generate a draft of the final output based on the user's submission and the rubric context.
    
When you receive a submission that includes feedback and suggested edits, do the following:
1. Review the feedback and suggested edits.
2. Revise your draft output to incorporate the feedback and suggested edits.
3. Generate a final output that meets the quality standards of the rubric.

# STYLE #
Your language should be clear, concise, and educational. Avoid jargon and ensure your output is structured, using headings and bullet points where appropriate.

# TONE #
Maintain an informative and professional tone throughout your output.

# AUDIENCE #
Hiring team members and hiring managers.

# RESPONSE #
[task_format]
"""

###############################################################################
# TASK_FORMAT_DEFINITIONS
###############################################################################
TASK_FORMAT_DEFINITIONS = {
    "Write a job description": """
Output should contain the following headings: "About Us, Job Summary, Key Responsibilities, Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment". 
Each section should build upon the previous ones to create a cohesive narrative. Use bullet points for Responsibilities, Requirements, and Benefits sections. 
Keep the About Us section under 150 words. Ensure all requirements listed are truly mandatory, including location and citizenship requirements when applicable. 
Always verify salary ranges comply with local pay transparency laws and reference specific technologies/tools rather than general terms whenever possible.
Ensure that your final output is evaluated against the quality standards provided in the rubric context above.
Follow the initial example below for the formatting of each section:

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
Output should contain a set of unique situational interview questions with follow-up questions based on provided interview competencies, information provided, and NexaTalent Pillars of Excellence. 
Ensure that each question reflects the quality and evaluation standards outlined in the rubric provided in the context.
Each question should be formatted as follows:

EXAMPLE:
>>User Summary: The user is seeking to create interview questions for a mid-level Nurse position at Care Partners in Omaha, NE. They have provided detailed information about the organization, job summary, key responsibilities, requirements, qualifications, key skills, benefits, salary, and work environment to guide the development of relevant interview questions that align with the competencies needed for the role.
>>Model Summary: The task of building interview questions involves creating a set of situational questions that assess candidates' competencies, experiences, and qualifications relevant to the mid-level Nurse position. These questions should be tailored to reflect the responsibilities and skills outlined in the job description and should help interviewers evaluate the suitability of candidates for the role.
>>Model Judgement: The tasks of the user and the model are highly similar, as both involve the creation of interview questions specifically designed for the Nurse position. The focus is on assessing the candidates' abilities and experiences related to the provided job details. Thus, I would score this a 5.
 
**Experience with Club Channel Sales**
Main Question: Can you describe a successful initiative you've led in the Club Channel space that delivered significant business growth? What was your role, and how did you measure success?
- Follow-up 1: How did you address challenges during this initiative, especially regarding broker partner management?
- Follow-up 2: What strategies did you use to ensure alignment across cross-functional teams?
""",
    "Create response guides": """
Objective: Generate a cohesive set of sample responses based on the NexaTalent rubric, ensuring each response reflects the corresponding level of proficiency.
Structure: For each main question, write five sample responses that align with levels 1 through 5 of the NexaTalent rubric. Label each response clearly as follows: Concern, Mild Concern, Mixed, Mild Strength, Strength.
Integration: Generate one unified set of samples for each question, incorporating responses to any follow-up questions as part of the final output.
Summary: After providing the sample responses, condense the overall summaries for each proficiency level into a format that is easily digestible, clearly differentiating the levels while maintaining the core insights about candidate competencies.
Clarity and Conciseness: Ensure that each response and summary is concise, avoids unnecessary jargon, and is written in an educational tone to facilitate understanding among hiring team members.
Ensure that your final set of responses adheres to the quality standards outlined in the rubric provided in the context.
    
Example Output:

**Question Set**
Describe a time when you identified and capitalized on a growth opportunity within a Club account, leading to mutual satisfaction and business expansion. How did you approach the partnership? 
- Follow-up 1: How did you align your strategies with the retailer's objectives to foster a cooperative relationship? 
- Follow-up 2: Can you share an example of how you handled a disagreement or challenge with a Club partner and turned it into a positive outcome? 

**Concern** 
- The candidate exhibits minimal understanding of growth opportunities and partnership dynamics, with vague and unclear responses. They avoid complexities and lack engagement with essential business concepts. They may be suitable for entry-level roles under close supervision and would require significant development to progress in more strategic positions.
**Mild Concern**
- This candidate reflects a limited understanding of key concepts related to growth and partnerships, often providing vague responses. They may recognize opportunities in theory but lack clear strategies for implementation. They would be suited for routine-oriented positions with considerable support and training needed to enhance their competencies.
**Mixed** 
- The candidate shows a basic grasp of growth opportunities, but their responses indicate reliance on routine practices and occasional gaps in strategic thinking. While they acknowledge challenges, they may struggle to align strategies with partner objectives. They could fit roles that allow for development while performing functional tasks but would benefit from additional coaching.
**Mild Strength** 
- This candidate demonstrates a solid understanding of growth opportunities and relationship-building, though they may not consistently leverage these effectively. They are capable and reliable but might lack the depth of analysis and proactive engagement found in higher proficiency levels. They would excel in supportive roles within account management with structured guidance.
**Strength** 
- The candidate is a proactive and results-oriented professional who seeks growth opportunities through thorough analysis and collaboration. They excel in building strong partnerships and effectively resolving challenges through constructive dialogue. Their ability to deliver measurable outcomes makes them an asset in business development and client management roles.
""",
    "Evaluate candidate responses": """
Output should be a numerical score between 1-5 grading the candidate's overall performance. This should be followed by a justification paragraph. 
There will also be a score of 1-5 for each individual question with justifications for the scoring.
For scoring, use the NexaTalent Rubric for Candidate Evaluation to assess and grade responses.
For justification paragraphs, cite examples from the candidate's response and connect them to the NexaTalent rubric as appropriate.
Ensure that your evaluation is strictly aligned with the quality standards outlined in the rubric provided in the context.
"""
}

###############################################################################
# Expandable Instructions
###############################################################################

TASK_INSTRUCTIONS = {
    "Write a job description": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Role Basics**
- Title: [job title and level (e.g., Senior Software Engineer)]
- Company Information: [Company name and description]
- Location: [work location, including remote options]

**Key Information**
- Primary Purpose: [brief description of the role's main objective]
- Must-Have Requirements: [2-3 critical qualifications or skills]
    """,
    
    "Build Interview Questions": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Role Context**
- Position: [job title and level]
- Key Skills: [2-3 most important skills to assess]
- Experience Level: [entry, mid, senior, etc.]

*>>NexaTip - You can input a job description for a more complete picture of this information*

**Interview Focus**
- Primary Competencies: [key competencies you want to evaluate]
- Specific Scenarios: [any particular situations you want to explore]
    """,
    
    "Create response guides": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Question Context**
- Interview Questions: [list the questions you need guides for]

**Key Criteria**
- Success Indicators: [what would make a response strong]
- Red Flags: [what would make a response concerning]

*>>NexaTip - Adding a job description gives us a better view of the role and how to assess quality responses.*
    """,
    
    "Evaluate candidate responses": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Context**
- Role: [position title and level]
- Questions Asked: [list of questions posed]
- Candidate Responses: [paste the responses to evaluate]

**Focus Areas**
- Key Requirements: [critical skills or competencies to assess]

*>>NexaTip - Adding a job description gives us a better view of the role and how to assess quality responses.*
    """
}

###############################################################################
# Streamlit UI and Integration
###############################################################################
# Replace text title with logo
st.image("reference_materials/Logo_Nexatalent_RGB.png", width=300)
st.subheader("Your assistant for generating high-quality hiring content.")

# Task selection
task = st.selectbox("Select a task:", list(ASSISTANT_IDS.keys()))

# Add the question text
st.write("How would you like to provide additional notes or information?")

# Create six columns but only use the first two
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Add buttons in the first two columns
with col1:
    if st.button("Paste text", type="primary"):
        st.session_state.input_method = "paste"
with col2:
    if st.button("Upload file"):
        st.session_state.input_method = "upload"

# Add the instructions expander after the buttons
with st.expander("Need help getting started?"):
    st.markdown(TASK_INSTRUCTIONS[task])

# Initialize session state for input method if not exists
if 'input_method' not in st.session_state:
    st.session_state.input_method = "paste"  # default to paste

# Show the appropriate input method based on selection
if st.session_state.input_method == "paste":
    user_notes = st.text_area("Enter additional notes or information:")
else:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md", "rtf", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
            user_notes = string_data.read()
        else:
            st.error("Currently, only plain text files are supported. Please upload a .txt file.")

@st.cache_data
def load_rubric(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return None

if st.button("Generate"):
    if not user_notes.strip():
        st.warning("Please provide text or upload a file with valid content.")
        st.stop()
    else:
        assistant_id = ASSISTANT_IDS[task]
        spinner_text = SPINNER_TEXTS[task]
        
        # Move review stage outside of spinner
        chosen_task_format = TASK_FORMAT_DEFINITIONS[task]
        chosen_task_overview = TASK_OVERVIEWS[task]
        chosen_task_look_fors = TASK_LOOK_FORS[task]

        rubric_mapping = {
            "Write a job description": "NexaTalent Rubric for Job Description Evaluation.txt",
            "Build Interview Questions": "NexaTalent Rubric for Interview Question Generation.txt",
            "Create response guides": "NexaTalent Rubric for Candidate Responses.txt",
            "Evaluate candidate responses": "NexaTalent Rubric for Candidate Responses.txt"
        }
        rubric_file_path = os.path.join("reference_materials", rubric_mapping.get(task, ""))
        rubric_context = load_rubric(rubric_file_path)
        if rubric_context is None:
            st.warning(f"Rubric file not found for task: {task}")
            rubric_context = ""
        
        # Review Stage
        review_user_summary, review_model_comparison, review_model_judgement = review_submission(
            user_notes, chosen_task_overview, chosen_task_look_fors, rubric_context
        )

        # Store these values in session state for fallback
        if "review_user_summary" not in st.session_state:
            st.session_state.review_user_summary = ""
        if "review_model_comparison" not in st.session_state:
            st.session_state.review_model_comparison = ""
        if "review_model_judgement" not in st.session_state:
            st.session_state.review_model_judgement = "0"

        st.session_state.review_user_summary = review_user_summary
        st.session_state.review_model_comparison = review_model_comparison
        st.session_state.review_model_judgement = review_model_judgement
        
        try:
            judgement_value = float(review_model_judgement)
        except ValueError:
            judgement_value = 0
        
        # Compute token counts even for warnings
        initial_submitted_text = f"USER NOTES:\n{user_notes}"
        initial_instructions = MASTER_INSTRUCTIONS.replace("[task_format]", chosen_task_format)
        initial_tokens = compute_tokens_for_stage(initial_instructions, initial_submitted_text)
        
        try:
            judgement_value = float(review_model_judgement)
        except ValueError:
            judgement_value = 0
        
        if judgement_value < 3:
            # Log the warning before showing the message to the user
            log_warning_to_google_sheets(
                tool_selection=task,
                user_input=user_notes,
                initial_submitted_tokens=initial_tokens["user"],
                initial_instructions_tokens=initial_tokens["system"],
                initial_prompt_tokens=initial_tokens["system"] + initial_tokens["user"],
                initial_output_tokens=0,  # No output was generated since we're stopping early
                user_summary=review_user_summary,
                model_comparison=review_model_comparison,
                model_judgement=review_model_judgement
            )

        if judgement_value < 3:
            st.warning(
                "It looks like you may be trying to complete a task that this tool hasn't yet been fine-tuned to handle. "
                "At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. "
                "This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.\n\n"
                "If you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com."
            )
            st.stop()
        
        # Only show spinner if review passes
        with st.spinner(spinner_text):
            try:
                # Define final_instructions before use
                final_instructions = (
                    "Rubric Context:\n" + rubric_context + "\n\n" +
                    MASTER_INSTRUCTIONS
                    .replace("[TASK_OVERVIEW]", chosen_task_overview)
                    .replace("[TASK_LOOK_FORS]", chosen_task_look_fors)
                    .replace("[task_format]", chosen_task_format.strip())
                    .replace("[confidentiality_message]", "It looks like you may be trying to complete a task that this tool hasn't yet been fine-tuned to handle. At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.\n\nIf you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com.")
                    + "\n\n"
                    "# ADDITIONAL NOTE #\n"
                    "Only provide the final output per the #RESPONSE# section. Do not include any chain-of-thought, steps, or internal reasoning. Do not include your own evaluations of your work in the final output. Do not indicate that the final version you generate has been revised or adapated based on feedback"
                )

                # -------------------------------
                # Step 1: Initial Generation
                # -------------------------------
                initial_submitted_text = f"USER NOTES:\n{user_notes}"
                # Compute token counts for the initial stage
                initial_tokens = compute_tokens_for_stage(final_instructions, initial_submitted_text)
                
                response_initial = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": initial_submitted_text}
                    ],
                    temperature=0.7
                )
                initial_output = response_initial.choices[0].message.content.strip()
                usage_initial = getattr(response_initial, "usage", None)
                if usage_initial:
                    initial_prompt_tokens = usage_initial.prompt_tokens
                    initial_completion_tokens = usage_initial.completion_tokens
                    initial_total_tokens = usage_initial.total_tokens
                else:
                    initial_prompt_tokens = initial_completion_tokens = initial_total_tokens = 0

                # -------------------------------
                # Step 2: Evaluation Stage
                # -------------------------------
                evaluator_instructions_text = EVALUATOR_INSTRUCTIONS
                evaluator_submitted_text = (
                    f"{EVALUATOR_INSTRUCTIONS}\n\n"
                    f"Rubric Context:\n{rubric_context}\n\n"
                    f"Content to Evaluate:\n{initial_output}\n\n"
                )
                evaluator_tokens = compute_tokens_for_stage(evaluator_instructions_text, evaluator_submitted_text)
                
                score, evaluator_feedback, evaluator_prompt_tokens, evaluator_completion_tokens, evaluator_total_tokens = evaluate_content(initial_output, rubric_context)

                # -------------------------------
                # Step 3: Final (Refinement) Stage
                # -------------------------------
                final_submitted_text = (
                    f"The following content was generated:\n{initial_output}\n\n"
                    f"The evaluator provided the following feedback:\n{evaluator_feedback}\n\n"
                    f"Please refine the content based on the feedback and ensure it follows this format:\n\n"
                    f"{TASK_FORMAT_DEFINITIONS[task]}\n\n"
                    "Important: Do not include any evaluation criteria, refinement notes, or improvement suggestions in the final output."
                )
                final_tokens = compute_tokens_for_stage(final_instructions, final_submitted_text)
                
                refined_response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": final_submitted_text}
                    ],
                    temperature=0.7
                )
                refined_output = refined_response.choices[0].message.content.strip()
                usage_final = getattr(refined_response, "usage", None)
                if usage_final:
                    final_prompt_tokens = usage_final.prompt_tokens
                    final_completion_tokens = usage_final.completion_tokens
                    final_total_tokens = usage_final.total_tokens
                else:
                    final_prompt_tokens = final_completion_tokens = final_total_tokens = 0

                # Compute overall total tokens (if needed)
                overall_total_tokens = initial_total_tokens + evaluator_total_tokens + final_total_tokens

                # Extract evaluation parts and actionable feedback
                user_summary, model_comparison, model_judgement = extract_evaluation_parts(refined_output)

                # Validate and ensure we have proper values
                user_summary, model_comparison, model_judgement = ensure_logging_values(
                    user_summary,
                    model_comparison,
                    model_judgement,
                    fallback_user_summary=st.session_state.review_user_summary,
                    fallback_model_comparison=st.session_state.review_model_comparison,
                    fallback_model_judgement=st.session_state.review_model_judgement
                )
                
                actionable_feedback = extract_actionable_feedback(evaluator_feedback)
                
                # Combine score and actionable feedback for logging
                feedback_text = (
                    f"Refinement based on evaluator score: {score}\n\n"
                    f"Actionable Feedback:\n{actionable_feedback}"
                )

                log_to_google_sheets(
                    tool_selection=task,
                    user_input=user_notes,
                    initial_output=initial_output,
                    evaluator_feedback=evaluator_feedback,
                    evaluator_score=score,
                    refined_output=refined_output,
                    initial_prompt_tokens=initial_prompt_tokens,
                    initial_completion_tokens=initial_completion_tokens,
                    evaluator_prompt_tokens=evaluator_prompt_tokens,
                    evaluator_completion_tokens=evaluator_completion_tokens,
                    final_prompt_tokens=final_prompt_tokens,
                    final_completion_tokens=final_completion_tokens,
                    overall_total_tokens=overall_total_tokens,
                    initial_instructions_tokens=initial_tokens["system"],
                    initial_submitted_tokens=initial_tokens["user"],
                    evaluator_instructions_tokens=evaluator_tokens["system"],
                    evaluator_submitted_tokens=evaluator_tokens["user"],
                    final_instructions_tokens=final_tokens["system"],
                    final_submitted_tokens=final_tokens["user"],
                    feedback=feedback_text,  # Updated to include actionable feedback
                    user_summary=user_summary,
                    model_comparison=model_comparison,
                    model_judgement=model_judgement
                )
                
                
                st.text_area("Generated Content", value=refined_output.strip(), height=400)
            except Exception as e:
                st.error(f"An error occurred during content generation: {str(e)}")
                print(f"Error details: {str(e)}")  # Log to console for debugging
                st.stop()

