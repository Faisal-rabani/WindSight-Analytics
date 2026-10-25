import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir.parent / ".env")
load_dotenv(basedir / ".env")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-wind-power-platform-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Elexon BMRS API Configuration
    ELEXON_BASE_URL = os.getenv("ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1")
    ELEXON_TIMEOUT_SECONDS = int(os.getenv("ELEXON_TIMEOUT_SECONDS", "30"))
    ELEXON_MAX_RETRIES = int(os.getenv("ELEXON_MAX_RETRIES", "3"))
    ELEXON_RETRY_BACKOFF = float(os.getenv("ELEXON_RETRY_BACKOFF", "1.5"))

    # Decision Logic Assumptions
    DECISION_CUTOFF_TIME = os.getenv("DECISION_CUTOFF_TIME", "10:00")
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Europe/London")
    ANALYSIS_PERIOD_START = os.getenv("ANALYSIS_PERIOD_START", "2026-01-01")
    ANALYSIS_PERIOD_END = os.getenv("ANALYSIS_PERIOD_END", "2026-01-31")

    # Data paths
    DATA_DIR = basedir / "data"
    PILOT_DB_PATH = DATA_DIR / "wind_forecast.db"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Default to SQLite database located in backend/data/
    default_db_uri = f"sqlite:///{Config.DATA_DIR / 'wind_forecast.db'}"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default_db_uri)


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Use bundled pilot database if DATABASE_URL not explicitly set
    default_prod_db = f"sqlite:///{Config.DATA_DIR / 'wind_forecast.db'}"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default_prod_db)


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
