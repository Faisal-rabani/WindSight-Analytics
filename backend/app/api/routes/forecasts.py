from flask import Blueprint, request
from app.api.responses import success_response, paginated_response, error_response
from app.services.forecast_service import ForecastService
from app.utils.validators import validate_date_range, validate_pagination_params

forecasts_bp = Blueprint("forecasts", __name__)
forecast_service = ForecastService()


@forecasts_bp.route("/comparison", methods=["GET"])
def get_comparison():
    """
    GET /api/v1/forecasts/comparison
    Returns matched forecast vs actual generation records with pagination.
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
        result = forecast_service.get_comparison(
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
        )
        return paginated_response(
            items=result["items"],
            total=result["total"],
            page=page,
            per_page=per_page,
            meta=result["meta"],
        )
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to retrieve forecast comparisons: {str(e)}", 500)


@forecasts_bp.route("/timeseries", methods=["GET"])
def get_timeseries():
    """
    GET /api/v1/forecasts/timeseries
    Returns full timeseries data for charting (forecast vs actual).
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        result = forecast_service.get_timeseries_all(
            start_date=start_date,
            end_date=end_date,
        )
        return success_response(data=result["timeseries"], meta=result["meta"])
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to retrieve timeseries data: {str(e)}", 500)
