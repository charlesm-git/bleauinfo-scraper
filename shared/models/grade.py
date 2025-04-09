from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, SmallInteger, String, select

from shared.models.base import Base
import shared.models.boulder


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    value: Mapped[str] = mapped_column(String(3))
    correspondence: Mapped[int] = mapped_column(SmallInteger)

    # Relationship
    boulders: Mapped[List["shared.models.boulder.Boulder"]] = relationship(
        back_populates="grade", foreign_keys="[Boulder.grade_id]"
    )
    slash_boulders: Mapped[List["shared.models.boulder.Boulder"]] = (
        relationship(
            back_populates="slash_grade",
            foreign_keys="[Boulder.slash_grade_id]",
        )
    )

    def __repr__(self):
        return f"<Grade : {self.value}, {self.correspondence}>"

    @classmethod
    def get_id_from_value(cls, db_session, grade_value):
        return db_session.scalar(
            select(cls.id).where(cls.value == grade_value)
        )
