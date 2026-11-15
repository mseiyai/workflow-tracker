from sqlalchemy import CheckConstraint, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'done')",
            name="ck_tasks_status_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    from datetime import datetime

    from sqlalchemy import DateTime, func

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )