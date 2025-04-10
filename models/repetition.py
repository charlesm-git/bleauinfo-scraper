from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey

from models.base import Base
import models.boulder
import models.user


class Repetition(Base):
    __tablename__ = "boulder_repetition"

    boulder_id: Mapped[int] = mapped_column(
        ForeignKey("boulder.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    log_date: Mapped[date] = mapped_column(Date)

    boulder: Mapped["models.boulder.Boulder"] = relationship(
        "Boulder", back_populates="repetitions"
    )
    user: Mapped["models.user.User"] = relationship(
        "User", back_populates="repetitions"
    )

    def __repr__(self):
        return f"<Repetition({self.user})"
