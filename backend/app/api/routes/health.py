from flask import Blueprint, current_app
from sqlalchemy import text
from app.extensions import db
from app.api.responses import success_response, error_response

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health endpoint returning application status and database readiness."""
    db_status = "healthy"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return success_response(
        data={
            "status": "online" if "unhealthy" not in db_status else "degraded",
            "service": "UK Wind Power Forecast Intelligence API",
            "version": "1.0.0",
            "database": db_status,
            "period": "2026-01",
            "decision_cutoff_time": current_app.config.get("DECISION_CUTOFF_TIME", "10:00"),
            "timezone": current_app.config.get("DEFAULT_TIMEZONE", "Europe/London"),
        }
    )
