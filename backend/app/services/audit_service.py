import json
from flask import request
from app.extensions import db
from app.models.audit import AuditLog

def log_audit_event(user_id: str, action: str, entity_type: str, entity_id: str, details_dict: dict = None):
    """Creates a persistent, immutable audit record."""
    try:
        ip = request.remote_addr if request else None
    except Exception:
        ip = None

    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=json.dumps(details_dict or {}) if details_dict else None,
        ip_address=ip
    )
    db.session.add(log_entry)
    db.session.commit()
    return log_entry
