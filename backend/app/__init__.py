import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, cors
from app.api.responses import error_response
from app.utils.logger import get_logger

logger = get_logger("app_factory")


def create_app(config_name: str = None) -> Flask:
    """Application factory for the Flask backend."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
    )

    # Register root / health routes
    @app.route("/")
    @app.route("/health")
    @app.route("/api")
    @app.route("/api/index")
    @app.route("/api/index.py")
    def index():
        from app.api.routes.health import health_check
        return health_check()

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Ensure tables exist (graceful fallback on read-only environments)
    with app.app_context():
        try:
            app.config["DATA_DIR"].mkdir(parents=True, exist_ok=True)
            db.create_all()
        except Exception as e:
            logger.warning(f"Database directory/table initialization skipped (read-only environment): {e}")

    # Wrap WSGI layer with VercelPathFixMiddleware to seamlessly restore paths on Vercel
    app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

    logger.info(f"Flask initialized in {config_name} mode. DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
    return app


class VercelPathFixMiddleware:
    """
    WSGI middleware that restores original PATH_INFO on Vercel.
    When vercel.json rewrites /:path* to /api/index?path=:path*,
    this middleware extracts the real requested path, restores PATH_INFO,
    and cleans up QUERY_STRING.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        from urllib.parse import parse_qs, urlencode, unquote

        qs = environ.get("QUERY_STRING", "")
        if qs:
            try:
                params = parse_qs(qs, keep_blank_values=True)
                for key in ("path", "_path"):
                    if key in params and params[key]:
                        raw_target = params.pop(key)[0]
                        target_path = unquote(raw_target)
                        if not target_path.startswith("/"):
                            target_path = "/" + target_path
                        while target_path.startswith("//"):
                            target_path = target_path[1:]
                        environ["PATH_INFO"] = target_path or "/"
                        environ["QUERY_STRING"] = urlencode(params, doseq=True)
                        break
            except Exception:
                pass

        return self.wsgi_app(environ, start_response)


def register_blueprints(app: Flask):
    """Register all API route blueprints with both /api/v1 and /v1 prefixes."""
    from app.api.routes.health import health_bp
    from app.api.routes.forecasts import forecasts_bp
    from app.api.routes.analytics import analytics_bp
    from app.api.routes.actuals import actuals_bp

    # Standard /api/v1 prefix
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(forecasts_bp, url_prefix="/api/v1/forecasts")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(actuals_bp, url_prefix="/api/v1/actuals")

    # Fallback /v1 prefix if a proxy or rewrite strips /api
    app.register_blueprint(health_bp, url_prefix="/v1", name="health_alt")
    app.register_blueprint(forecasts_bp, url_prefix="/v1/forecasts", name="forecasts_alt")
    app.register_blueprint(analytics_bp, url_prefix="/v1/analytics", name="analytics_alt")
    app.register_blueprint(actuals_bp, url_prefix="/v1/actuals", name="actuals_alt")


def register_error_handlers(app: Flask):
    """Register centralized error handlers."""
    @app.errorhandler(400)
    def bad_request(e):
        return error_response(str(e.description or "Bad request"), 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("The requested resource was not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("Method not allowed", 405)

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return error_response("An internal server error occurred", 500)

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return error_response(str(e), 400)
