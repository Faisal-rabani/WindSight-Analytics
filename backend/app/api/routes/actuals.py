from datetime import datetime, time, timezone
from flask import Blueprint, request
from app.api.responses import success_response, paginated_response, error_response
from app.repositories.actual_repository import ActualRepository
from app.utils.validators import validate_date_range, validate_pagination_params

actuals_bp = Blueprint("actuals", __name__)


@actuals_bp.route("", methods=["GET"])
def get_actuals():
    """
    GET /api/v1/actuals
    Returns actual wind generation records with optional date filtering and pagination.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        page, per_page = validate_pagination_params(
            request.args.get("page"),
            request.args.get("per_page"),
        )

        start_dt_utc = datetime.combine(start_date, time(0, 0), tzinfo=timezone.utc)
        end_dt_utc = datetime.combine(end_date, time(23, 59, 59), tzinfo=timezone.utc)

        total = ActualRepository.get_count_in_range(start_dt_utc, end_dt_utc, fuel_type="WIND")
        all_actuals = ActualRepository.get_in_range(start_dt_utc, end_dt_utc, fuel_type="WIND")

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        items = [a.to_dict() for a in all_actuals[start_idx:end_idx]]

        return paginated_response(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            meta={"start_date": str(start_date), "end_date": str(end_date)},
        )
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to retrieve actuals: {str(e)}", 500)
