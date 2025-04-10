from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String

from models.base import Base
from models.boulder_setter import boulder_setter_table
import models.boulder
import models.repetition

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, unique=True)

    # Relationship
    set_boulders: Mapped[List["models.boulder.Boulder"]] = relationship(
        secondary=boulder_setter_table, back_populates="setters"
    )
    repetitions: Mapped[List["models.repetition.Repetition"]] = relationship(
        "Repetition", back_populates="user"
    )

    def __repr__(self):
        return f"<User(id: {self.id}, username: {self.username})>"
