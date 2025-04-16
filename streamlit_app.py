# Updated main.py with token logging fixes and debug preview
import streamlit as st
from session_state import init_session_state
from config import ASSISTANT_IDS, RUBRIC_FILENAMES, TASK_OVERVIEWS, TASK_LOOK_FORS
from prompts.task_instructions import TASK_INSTRUCTIONS
from prompts.evaluators import EVALUATOR_INSTRUCTIONS, CR_EVALUATOR_INSTRUCTIONS
from utils.file_io import extract_text_from_file
from utils.logger import log_consent
from utils.logger_helper import log_final_success, log_review_warning
from utils.reviewer import review_submission, evaluate_generated_draft
from utils.token_utils import compute_tokens_for_stage, count_tokens
from generators.rewriter import revise_draft_with_feedback
from generators.job_description import generate_job_description
from generators.interview_questions import generate_interview_questions
from generators.response_guides import generate_response_guides
from generators.candidate_eval import generate_candidate_evaluation
from docx import Document
from io import BytesIO
import os
import re
import json

TOOL_OUTPUT_TITLES = {
    "Write a job description": "Job Description",
    "Build Interview Questions": "Interview Questions",
    "Create response guides": "Candidate Response Guide",
    "Evaluate candidate responses": "Evaluation Summary"
}

def extract_score(evaluation_text):
    match = re.search(r"Score:\s*([0-5](?:\.\d+)?)", evaluation_text)
    return float(match.group(1)) if match else None

if "reset_triggered" in st.session_state:
    # Preserve consent and user email
    consent_status = st.session_state.get("consent_accepted", False)
    user_email = st.session_state.get("user_email", "")

    # Clear everything else
    keys_to_keep = {"consent_accepted", "user_email"}
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

    # Restore preserved values
    st.session_state["consent_accepted"] = consent_status
    st.session_state["user_email"] = user_email

    st.rerun()

st.set_page_config(page_title="NexaTalent AI", layout="wide")
init_session_state()

if "consent_accepted" not in st.session_state:
    st.session_state.consent_accepted = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if not st.session_state.consent_accepted:
    with open("utils/consent_screen.txt", "r", encoding="utf-8") as f:
        consent_text = f.read()
    st.image("reference_materials/Logo_Nexatalent_RGB.png", width=200)
    st.markdown("## Consent Required to Continue")
    st.markdown(consent_text)
    email = st.text_input("Enter your email address to proceed:")
    valid_email = re.match(r"[^@]+@[^@]+\.[^@]+", email)

    if st.button("I Consent", disabled=not valid_email):
        response = log_consent(email)
        if response:
            st.session_state.consent_accepted = True
            st.session_state.user_email = email
            st.success("✅ Thank you! You're all set.")
            st.rerun()
        else:
            st.error("There was a problem logging your consent. Please try again.")
    st.stop()

st.image("reference_materials/Logo_Nexatalent_RGB.png", width=300)
st.subheader("Your assistant for generating high-quality hiring content.")

st.sidebar.header("Tools")
task = st.sidebar.selectbox(
    "Select a task:", 
    list(ASSISTANT_IDS.keys()), 
    #disabled=st.session_state.get("generated_complete", False)
)

st.sidebar.header("Controls")
generate_disabled = st.session_state.get("generated_complete", False) and "final_output" in st.session_state
if st.sidebar.button("Generate", use_container_width=True, type="primary", key="generate"):
    st.session_state.generate_clicked = True
    st.session_state.generated_complete = False

if st.sidebar.button("Reset Tool", use_container_width=True, key="reset"):
    st.session_state.reset_triggered = True
    st.rerun()
st.sidebar.markdown("---")

if "token_usage" not in st.session_state:
    st.session_state.token_usage = {}

if not st.session_state.get("generated_complete", False):
    status_container = st.sidebar.container()
else:
    docx_buffer = st.session_state.get("docx_buffer")
    if docx_buffer:
        # Get the specific title for the current task
        output_title = TOOL_OUTPUT_TITLES.get(task, "Final Output")
        
        st.sidebar.download_button(
            f"\U0001F4BE Download {output_title} (.docx)",
            docx_buffer,
            file_name=f"{output_title}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="download_docx"
        )
        
        # Add clipboard copy functionality - properly in sidebar
        if st.session_state.get("final_output"):
            from streamlit.components.v1 import html
            copy_button_html = f"""
            <script>
            function copyToClipboard() {{
                const text = `{st.session_state.final_output.replace("`", "\\`").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")}`;
                navigator.clipboard.writeText(text).then(function() {{
                    const successMsg = document.getElementById('copy-message');
                    successMsg.innerHTML = '✅ Copied to clipboard!';
                    successMsg.style.display = 'block';
                    successMsg.style.backgroundColor = '#d4edda';
                    successMsg.style.color = '#155724';
                    successMsg.style.padding = '8px';
                    successMsg.style.borderRadius = '4px';
                    successMsg.style.marginTop = '10px';
                    successMsg.style.textAlign = 'center';
                    successMsg.style.border = '1px solid #c3e6cb';
                    
                    setTimeout(function() {{
                        successMsg.style.display = 'none';
                    }}, 3000);
                }})
                .catch(function() {{
                    const errorMsg = document.getElementById('copy-message');
                    errorMsg.innerHTML = '❌ Failed to copy';
                    errorMsg.style.display = 'block';
                    errorMsg.style.backgroundColor = '#f8d7da';
                    errorMsg.style.color = '#721c24';
                    errorMsg.style.padding = '8px';
                    errorMsg.style.borderRadius = '4px';
                    errorMsg.style.marginTop = '10px';
                    errorMsg.style.textAlign = 'center';
                    errorMsg.style.border = '1px solid #f5c6cb';
                    
                    setTimeout(function() {{
                        errorMsg.style.display = 'none';
                    }}, 3000);
                }});
            }}
            </script>
            <button onclick="copyToClipboard()" style="width:100%; padding:8px; margin:5px 0; background-color:#f0f2f6; border:1px solid #ccc; border-radius:4px; cursor:pointer;">
                📋 Copy Text to Clipboard
            </button>
            <div id="copy-message" style="display:none; margin-bottom:10px;"></div>
            """
            # Use sidebar's container to ensure the HTML component is in the sidebar
            sidebar_container = st.sidebar.container()
            with sidebar_container:
                html(copy_button_html, height=100)

st.write("How would you like to provide additional notes or information?")
col1, col2, *_ = st.columns(6)
with col1:
    if st.button("Paste text", type="primary"):
        st.session_state.input_method = "paste"
with col2:
    if st.button("Upload file"):
        st.session_state.input_method = "upload"

user_notes = ""
if st.session_state.input_method == "paste":
    user_notes = st.text_area("Enter additional notes or information:")

    # Show instructions help only when pasting
    show_help_expander = (
        st.session_state.get("input_method") == "paste"
        and not st.session_state.get("generate_clicked", False)
        and not st.session_state.get("review_user_summary")
        and not st.session_state.get("initial_draft")
        and not st.session_state.get("evaluation")
        and not st.session_state.get("final_output")
    )

    if show_help_expander:
        with st.expander("Need help getting started?"):
            st.markdown(TASK_INSTRUCTIONS[task])

elif st.session_state.input_method == "upload":
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "md", "docx", "pdf"])
    if uploaded_file:
        user_notes = extract_text_from_file(uploaded_file)
        st.success(f"Successfully extracted text from {uploaded_file.name}")
        #with st.expander("Preview extracted content"):
        #    st.text(user_notes[:500] + ("..." if len(user_notes) > 500 else ""))


if st.session_state.get("review_blocked"):
    st.warning(st.session_state.review_warning)
    st.stop()

if st.session_state.get("generate_clicked", False) and not st.session_state.get("generated_complete", False):

    if not user_notes.strip():
        st.warning("Please provide input before generating content.")
        st.stop()

###########################################################
## CONTENT GENERATION ## 
###########################################################

#################### REVIEW SUBMISSION ####################

    with status_container.status("Reviewing submission", expanded=True):
        rubric_path = f"reference_materials/{RUBRIC_FILENAMES[task]}"
        with open(rubric_path, "r", encoding="utf-8") as f:
            rubric_context = f.read()
        overview = TASK_OVERVIEWS[task]
        look_fors = TASK_LOOK_FORS[task]

        summary, comparison, judgement = review_submission(user_notes, overview, look_fors, rubric_context)
        st.session_state.review_user_summary = summary
        st.session_state.review_model_comparison = comparison
        st.session_state.review_model_judgement = judgement

        token_info = compute_tokens_for_stage(rubric_context, user_notes)
        st.session_state.token_usage.update({
            "initial_user_tokens": token_info["user"],
            "initial_instructions_tokens": token_info["system"],
            "initial_prompt_tokens_total": token_info["user"] + token_info["system"]
        })

        try:
            score = float(judgement)
        except:
            score = 0.0

        if score > 3:
            log_review_warning(task, user_notes)
            st.session_state.review_blocked = True
            st.session_state.review_warning = "\u26a0\ufe0f Your input doesn't align with the selected tool. Please revise your notes or select a different option."
            st.stop()

#################### INITIAL DRAFT ####################

    with status_container.status("Generating initial draft", expanded=True):
        if task == "Write a job description":
            result = generate_job_description(user_notes, rubric_context)
        elif task == "Build Interview Questions":
            result = generate_interview_questions(user_notes, rubric_context)
        elif task == "Create response guides":
            result = generate_response_guides(user_notes, rubric_context)
        elif task == "Evaluate candidate responses":
            result = generate_candidate_evaluation(user_notes, rubric_context)
        else:
            result = "Task not recognized."
        st.session_state.initial_draft = result
        st.session_state.token_usage["initial_output_tokens"] = count_tokens(result)

    #with st.expander("Initial Draft Output"):
    #    st.markdown(st.session_state.initial_draft)

###################### EVALUATOR ######################

    with status_container.status("Evaluating content", expanded=True):
        evaluation_result = evaluate_generated_draft(
            content=st.session_state.initial_draft,
            rubric=rubric_context,
            task=task
        )
        st.session_state.evaluation = evaluation_result
        st.session_state.token_usage["evaluator_output_tokens"] = count_tokens(evaluation_result)
        st.session_state.token_usage["evaluator_prompt_tokens_total"] = count_tokens(rubric_context + st.session_state.initial_draft)
        st.session_state.token_usage["evaluator_submitted_tokens"] = count_tokens(st.session_state.initial_draft)
        st.session_state.token_usage["evaluator_instructions_tokens"] = count_tokens(EVALUATOR_INSTRUCTIONS)
        st.session_state.evaluator_score = extract_score(evaluation_result)

    #with st.expander("Content Evaluation"):
    #    st.markdown(st.session_state.evaluation)

###################### REVISON ######################

    with status_container.status("Revising final version", expanded=True):
        final = revise_draft_with_feedback(
            draft=st.session_state.initial_draft,
            evaluation=st.session_state.evaluation,
            rubric=rubric_context,
            task=task
        )
        st.session_state.final_output = final
        st.session_state.token_usage["revision_instructions_tokens"] = count_tokens(rubric_context)
        st.session_state.token_usage["revision_submitted_tokens"] = count_tokens(st.session_state.initial_draft + st.session_state.evaluation)
        st.session_state.token_usage["revision_output_tokens"] = count_tokens(final)
        st.session_state.token_usage["revision_prompt_tokens_total"] = count_tokens(st.session_state.initial_draft + st.session_state.evaluation + rubric_context)

    doc = Document()
    doc.add_paragraph(st.session_state.final_output)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.session_state.docx_buffer = buffer

    st.session_state.total_tokens = sum(st.session_state.token_usage.values())
    st.session_state.evaluator_feedback = st.session_state.evaluation
    st.session_state.refined_output = st.session_state.final_output

    log_final_success(task, user_notes)
    st.session_state.generated_complete = True

    #st.markdown("### ✨ Debug Log Preview")
    #debug_log = {
    #    "initial_generated_output": st.session_state.get("initial_draft", ""),
    #    "evaluator_feedback": st.session_state.get("evaluation", ""),
    #    "final_refined_output": st.session_state.get("final_output", ""),
    #    "evaluator_score": st.session_state.get("evaluator_score", ""),
    #    "total_tokens": st.session_state.get("total_tokens", 0),
    #    "token_usage": st.session_state.get("token_usage", {}),
    #    "user_summary": st.session_state.get("review_user_summary", ""),
    #    "model_comparison": st.session_state.get("review_model_comparison", ""),
    #    "model_judgement": st.session_state.get("review_model_judgement", ""),
    #    "revision_submitted_tokens": st.session_state.token_usage.get("revision_submitted_tokens", "MISSING"),
    #    "revision_instructions_tokens": st.session_state.token_usage.get("revision_instructions_tokens", "MISSING")
    
    #}
    #st.code(json.dumps(debug_log, indent=2))
    st.rerun()

if st.session_state.get("generated_complete", False) and st.session_state.get("final_output"):
    st.markdown("---")
    st.header("Your Generated Content")
    st.subheader(f"**{TOOL_OUTPUT_TITLES[task]}**\n")
    st.write(st.session_state.final_output)

