from flask import Blueprint, request
from app.api.responses import success_response, error_response
from app.services.analytics_service import AnalyticsService
from app.utils.validators import validate_date_range

analytics_bp = Blueprint("analytics", __name__)
analytics_service = AnalyticsService()


@analytics_bp.route("/overview", methods=["GET"])
def get_overview():
    """
    GET /api/v1/analytics/overview
    Returns executive metrics summary for dashboard overview.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        overview = analytics_service.get_overview(start_date, end_date)
        return success_response(data=overview)
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to generate overview analytics: {str(e)}", 500)


@analytics_bp.route("/daily", methods=["GET"])
def get_daily():
    """
    GET /api/v1/analytics/daily
    Returns daily MAE, RMSE, bias, and coverage.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        daily_data = analytics_service.get_daily_accuracy(start_date, end_date)
        return success_response(data=daily_data["days"], meta=daily_data["meta"])
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to generate daily accuracy analytics: {str(e)}", 500)


@analytics_bp.route("/distribution", methods=["GET"])
def get_distribution():
    """
    GET /api/v1/analytics/distribution
    Returns histogram bins and counts for forecast errors.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        bins_param = int(request.args.get("bins", 12))
        dist_data = analytics_service.get_error_distribution(start_date, end_date, num_bins=bins_param)
        return success_response(data=dist_data["bins"], meta={
            "total_samples": dist_data.get("total_samples", 0),
            "min_error_mw": dist_data.get("min_error_mw", 0),
            "max_error_mw": dist_data.get("max_error_mw", 0),
            **dist_data.get("meta", {}),
        })
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to generate error distribution: {str(e)}", 500)


@analytics_bp.route("/extremes", methods=["GET"])
def get_extremes():
    """
    GET /api/v1/analytics/extremes
    Returns intervals with the largest forecast errors.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        top_n = int(request.args.get("limit", 15))
        extremes_data = analytics_service.get_extreme_errors(start_date, end_date, top_n=top_n)
        return success_response(data=extremes_data["extremes"], meta=extremes_data["meta"])
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to generate extreme errors: {str(e)}", 500)


@analytics_bp.route("/quality", methods=["GET"])
def get_quality():
    """
    GET /api/v1/analytics/quality
    Returns data quality and completeness indicators.
    """
    try:
        start_date, end_date = validate_date_range(
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        quality_data = analytics_service.get_data_quality(start_date, end_date)
        return success_response(data=quality_data)
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        return error_response(f"Failed to generate data quality report: {str(e)}", 500)
