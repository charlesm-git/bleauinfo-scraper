from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String

from models.base import Base
import models.boulder

class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String(3))
    correspondence: Mapped[int] = mapped_column(SmallInteger)

    # Relationship
    boulders: Mapped[List["models.boulder.Boulder"]] = relationship(
        back_populates="grade"
    )

    def __repr__(self):
        return f"<Grade : {self.value}, {self.correspondence}>"