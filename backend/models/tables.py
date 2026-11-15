from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class MetricCatalog(Base):
    """Canonical catalog entry corresponding to one of the 32 CSV files."""

    __tablename__ = "metric_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    dataset_key: Mapped[str] = mapped_column(String(96), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(48), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="metric",
        cascade="all, delete-orphan",
    )


class Astronaut(Base):
    __tablename__ = "astronauts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="astronaut",
        cascade="all, delete-orphan",
    )


class Measurement(Base):
    """One source CSV row; variable fields remain intact in JSON."""

    __tablename__ = "measurements"
    __table_args__ = (
        Index(
            "ix_measurements_astronaut_metric_time",
            "astronaut_id",
            "metric_id",
            "recorded_at",
        ),
        UniqueConstraint(
            "astronaut_id",
            "metric_id",
            "record_id",
            name="uq_measurement_subject_metric_record",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astronaut_id: Mapped[str] = mapped_column(
        ForeignKey("astronauts.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric_id: Mapped[int] = mapped_column(
        ForeignKey("metric_catalog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    record_id: Mapped[str] = mapped_column(String(120), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    values_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)

    astronaut: Mapped[Astronaut] = relationship(back_populates="measurements")
    metric: Mapped[MetricCatalog] = relationship(back_populates="measurements")
