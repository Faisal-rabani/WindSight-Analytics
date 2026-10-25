from datetime import datetime, timezone
from app.extensions import db


class ActualGeneration(db.Model):
    """
    Actual wind generation from Elexon FUELHH dataset.
    Preserves exact settlement intervals (30 min) in MW.
    """
    __tablename__ = "actual_generation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time_utc = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    fuel_type = db.Column(db.String(32), nullable=False, default="WIND", index=True)
    generation_mw = db.Column(db.Float, nullable=False)
    settlement_date = db.Column(db.String(10), nullable=True, index=True)
    settlement_period = db.Column(db.Integer, nullable=True)
    ingested_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("start_time_utc", "fuel_type", name="uq_actual_start_fuel"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "start_time_utc": self.start_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ") if self.start_time_utc else None,
            "fuel_type": self.fuel_type,
            "generation_mw": round(self.generation_mw, 2),
            "settlement_date": self.settlement_date,
            "settlement_period": self.settlement_period,
            "ingested_at": self.ingested_at.strftime("%Y-%m-%dT%H:%M:%SZ") if self.ingested_at else None,
        }

    def __repr__(self):
        return f"<ActualGeneration id={self.id} start={self.start_time_utc} mw={self.generation_mw}>"
