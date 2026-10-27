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
    When vercel.json rewrites /:path* to /api/index?path=:path*,
    this middleware extracts the real requested path, restores PATH_INFO,
    and cleans up QUERY_STRING.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        if query_string:
            try:
                params = parse_qs(query_string, keep_blank_values=True)
                for key in ("path", "_path"):
                    if key in params and params[key]:
                        target_path = params.pop(key)[0]
                        if not target_path.startswith("/"):
                            target_path = "/" + target_path
                        while target_path.startswith("//"):
                            target_path = target_path[1:]
                        environ["PATH_INFO"] = target_path or "/"
                        environ["QUERY_STRING"] = urlencode(params, doseq=True)
                        break
            except Exception:
                pass

        # Fallback to matched path headers if available
        matched_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_VERCEL_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
        )
        if matched_path and matched_path not in ("/api/index", "/api/index.py"):
            path_only = matched_path.split("?")[0]
            if path_only not in ("/", "/api/index"):
                environ["PATH_INFO"] = path_only

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelRewriteMiddleware(app.wsgi_app)

