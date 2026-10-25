from flask import jsonify, Response
from typing import Any, Optional, Dict, List


def success_response(
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> Response:
    """Builds a standardized success JSON response."""
    payload = {
        "status": "success",
        "data": data,
    }
    if meta is not None:
        payload["meta"] = meta
    response = jsonify(payload)
    response.status_code = status_code
    return response


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> Response:
    """Builds a standardized paginated JSON response."""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    pagination = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
    response_meta = {**pagination, **(meta or {})}
    return success_response(data=items, meta=response_meta, status_code=status_code)


def error_response(
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
) -> Response:
    """Builds a standardized error JSON response."""
    payload = {
        "status": "error",
        "error": {
            "code": status_code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    response = jsonify(payload)
    response.status_code = status_code
    return response
