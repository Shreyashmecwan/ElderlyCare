import re
from datetime import datetime, date
from flask import jsonify

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
TIME_REGEX = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"

def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def is_valid_time(time_str: str) -> bool:
    if not time_str or not isinstance(time_str, str):
        return False
    return bool(re.match(TIME_REGEX, time_str.strip()))

def is_valid_date(date_str: str) -> bool:
    if not date_str or not isinstance(date_str, str):
        return False
    if not re.match(DATE_REGEX, date_str.strip()):
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def parse_date(date_str: str) -> date | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except Exception:
        return None

def api_response(data=None, message: str = "", status_code: int = 200):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    if message:
        payload["message"] = message
    return jsonify(payload), status_code

def api_error(message: str, code: str = "BAD_REQUEST", status_code: int = 400, details=None):
    err = {
        "code": code,
        "message": message
    }
    if details:
        err["details"] = details
    return jsonify({"success": False, "error": err}), status_code
