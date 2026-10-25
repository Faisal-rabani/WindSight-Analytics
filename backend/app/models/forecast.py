from datetime import datetime, timezone
from app.extensions import db


class WindForecast(db.Model):
    """
    Wind power forecasts from Elexon WINDFOR dataset.
    Preserves all historical forecast publication versions.
    """
    __tablename__ = "wind_forecasts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time_utc = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    publish_time_utc = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    generation_mw = db.Column(db.Float, nullable=False)
    ingested_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("start_time_utc", "publish_time_utc", name="uq_forecast_start_publish"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "start_time_utc": self.start_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ") if self.start_time_utc else None,
            "publish_time_utc": self.publish_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ") if self.publish_time_utc else None,
            "generation_mw": round(self.generation_mw, 2),
            "ingested_at": self.ingested_at.strftime("%Y-%m-%dT%H:%M:%SZ") if self.ingested_at else None,
        }

    def __repr__(self):
        return (
            f"<WindForecast id={self.id} start={self.start_time_utc} "
            f"pub={self.publish_time_utc} mw={self.generation_mw}>"
        )
