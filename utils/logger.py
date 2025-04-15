# utils/logger.py

import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from config import MAIN_LOGGER_URL, WARNING_LOGGER_URL, CONSENT_TRACKER_URL


def get_current_timestamp():
    return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m/%d/%Y %I:%M:%S %p")


def log_consent(email):
    data = {
        "timestamp": get_current_timestamp(),
        "email": email,
        "consent": "I agree",
        "ip_address": ""
    }
    try:
        return requests.post(CONSENT_TRACKER_URL, json=data).text
    except Exception as e:
        print(f"Consent logging error: {str(e)}")
        return None


def log_warning_to_google_sheets(**kwargs):
    data = {"log_type": "warning", "timestamp": get_current_timestamp(), **kwargs}
    try:
        return requests.post(WARNING_LOGGER_URL, json=data).text
    except Exception as e:
        return f"Warning logging error: {e}"


def log_to_google_sheets(**kwargs):
    data = {"timestamp": get_current_timestamp(), **kwargs}
    try:
        return requests.post(MAIN_LOGGER_URL, json=data).text
    except Exception as e:
        return f"Logging error: {e}"
