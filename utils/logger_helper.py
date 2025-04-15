# utils/logger_helper.py

from utils.logger import log_to_google_sheets, log_warning_to_google_sheets

def safe_get(key, default=""):
    import streamlit as st
    return st.session_state.get(key, default)

def get_token_value(key):
    return safe_get("token_usage", {}).get(key, 0)

def log_final_success(task, user_input):
    import streamlit as st
    from utils.logger import log_to_google_sheets

    # Required fields from session state
    initial_output = st.session_state.get("initial_draft", "")
    evaluator_feedback = st.session_state.get("evaluation", "")
    refined_output = st.session_state.get("final_output", "")
    evaluator_score = st.session_state.get("evaluator_score", "")

    # Token data
    token_data = st.session_state.get("token_usage", {})
    initial_prompt_tokens = token_data.get("initial_prompt_tokens_total", 0)
    initial_completion_tokens = token_data.get("initial_output_tokens", 0)
    evaluator_prompt_tokens = token_data.get("evaluator_prompt_tokens_total", 0)
    evaluator_completion_tokens = token_data.get("evaluator_output_tokens", 0)
    final_prompt_tokens = token_data.get("revision_prompt_tokens_total", 0)
    final_completion_tokens = token_data.get("revision_output_tokens", 0)
    overall_total_tokens = sum(token_data.values())

    # Extra submitted/instructions breakdown
    initial_instructions_tokens = token_data.get("initial_instructions_tokens", 0)
    initial_submitted_tokens = token_data.get("initial_user_tokens", 0)
    evaluator_instructions_tokens = token_data.get("evaluator_instructions_tokens", 0)
    evaluator_submitted_tokens = token_data.get("evaluator_submitted_tokens", 0)
    final_instructions_tokens = token_data.get("revision_instructions_tokens", 0)
    final_submitted_tokens = token_data.get("revision_submitted_tokens", 0)

    # Metadata
    user_summary = st.session_state.get("review_user_summary", "")
    model_comparison = st.session_state.get("review_model_comparison", "")
    model_judgement = st.session_state.get("review_model_judgement", "")

    # Send to Google Sheets
    response = log_to_google_sheets(
        tool_selection=task,
        user_input=user_input,
        initial_output=initial_output,
        evaluator_feedback=evaluator_feedback,
        evaluator_score=evaluator_score,
        refined_output=refined_output,
        initial_submitted_tokens=initial_submitted_tokens,
        initial_instructions_tokens=initial_instructions_tokens,
        initial_prompt_tokens=initial_prompt_tokens,
        initial_completion_tokens=initial_completion_tokens,
        evaluator_submitted_tokens=evaluator_submitted_tokens,
        evaluator_instructions_tokens=evaluator_instructions_tokens,
        evaluator_prompt_tokens=evaluator_prompt_tokens,
        evaluator_completion_tokens=evaluator_completion_tokens,
        final_submitted_tokens=final_submitted_tokens,
        final_instructions_tokens=final_instructions_tokens,
        final_prompt_tokens=final_prompt_tokens,
        final_completion_tokens=final_completion_tokens,
        overall_total_tokens=overall_total_tokens,
        ip_address="",
        feedback="",
        user_summary=user_summary,
        model_comparison=model_comparison,
        model_judgement=model_judgement
    )

    print("Log submission response:", response)


def log_review_warning(task, user_notes):
    log_warning_to_google_sheets(
        tool_selection=task,
        user_input=user_notes,
        initial_submitted_tokens=get_token_value("initial_user_tokens"),
        initial_instructions_tokens=get_token_value("initial_instructions_tokens"),
        initial_prompt_tokens_total=get_token_value("initial_prompt_tokens_total"),
        user_summary=safe_get("review_user_summary"),
        model_comparison=safe_get("review_model_comparison"),
        model_judgement=safe_get("review_model_judgement")
    )
