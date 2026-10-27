import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app

app = create_app("production")


class VercelRewriteMiddleware:
    """
    WSGI middleware that restores original PATH_INFO on Vercel.
    When vercel.json rewrites /(.*) to /api/index, Vercel sets
    HTTP_X_MATCHED_PATH or HTTP_X_FORWARDED_URI to the original client URL.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_VERCEL_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
        )
        if matched_path and matched_path not in ("/api/index", "/api/index.py"):
            environ["PATH_INFO"] = matched_path.split("?")[0]
        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelRewriteMiddleware(app.wsgi_app)

