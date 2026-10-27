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

    from flask import request
    
    debug_routing = {
        "request_path": request.path,
        "x_matched_path": request.headers.get("x-matched-path"),
        "x_forwarded_uri": request.headers.get("x-forwarded-uri"),
        "x_vercel_path": request.headers.get("x-vercel-path"),
        "matched_keys": [k for k in request.environ.keys() if any(t in k.lower() for t in ["match", "path", "uri", "route", "forward"])],
    }

    return success_response(
        data={
            "status": "online" if "unhealthy" not in db_status else "degraded",
            "service": "UK Wind Power Forecast Intelligence API",
            "version": "1.0.0",
            "database": db_status,
            "period": "2026-01",
            "decision_cutoff_time": current_app.config.get("DECISION_CUTOFF_TIME", "10:00"),
            "timezone": current_app.config.get("DEFAULT_TIMEZONE", "Europe/London"),
            "routing": debug_routing,
        }
    )
