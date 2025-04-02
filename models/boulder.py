from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Integer, String, ForeignKey

from models.base import Base
import models.grade
import models.area


class Boulder(Base):
    __tablename__ = "boulder"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id"))
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    setter: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    url: Mapped[str] = mapped_column(String)
    number_of_repetition: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    grade: Mapped["models.grade.Grade"] = relationship(
        "Grade", back_populates="boulders"
    )
    area: Mapped["models.area.Area"] = relationship(
        "Area", back_populates="boulders"
    )

    def __repr__(self):
        return f"<Boulder(name: {self.name}, grade: {self.grade}, setter: {self.setter}, style: {self.style}, nb_of_rep: {self.number_of_repetitions}, rating: {self.rating})>"

    def as_list(self):
        return [
            self.name,
            self.grade,
            self.area,
            self.setter,
            self.rating,
            self.number_of_repetitions,
            self.style,
            self.url,
        ]
