import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app

app = create_app("production")


from urllib.parse import parse_qs, urlencode


class VercelRewriteMiddleware:
    """
    WSGI middleware that restores original PATH_INFO on Vercel.
    When vercel.json rewrites /(.*) to /api/index?_path=/$1,
    this middleware extracts the real requested path, restores PATH_INFO,
    and cleans up QUERY_STRING.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check for _path forwarded via vercel.json rewrite
        query_string = environ.get("QUERY_STRING", "")
        if "_path=" in query_string:
            try:
                params = parse_qs(query_string, keep_blank_values=True)
                if "_path" in params and params["_path"]:
                    target_path = params.pop("_path")[0]
                    if not target_path.startswith("/"):
                        target_path = "/" + target_path
                    while target_path.startswith("//"):
                        target_path = target_path[1:]
                    environ["PATH_INFO"] = target_path or "/"
                    environ["QUERY_STRING"] = urlencode(params, doseq=True)
            except Exception:
                pass

        # 2. Fallback to matched path headers if available
        matched_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_VERCEL_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
        )
        if matched_path and matched_path not in ("/api/index", "/api/index.py") and not query_string.startswith("_path="):
            environ["PATH_INFO"] = matched_path.split("?")[0]

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelRewriteMiddleware(app.wsgi_app)

