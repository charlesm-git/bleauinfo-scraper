from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, Float, Integer, String, ForeignKey

from models.base import Base
import models.grade
import models.area

boulder_style_table = Table(
    "boulder_style",
    Base.metadata,
    Column("boulder_id", ForeignKey("boulder.id"), primary_key=True),
    Column("style_id", ForeignKey("style.id"), primary_key=True),
)

boulder_setter_table = Table(
    "boulder_setter",
    Base.metadata,
    Column("boulder_id", ForeignKey("boulder.id"), primary_key=True),
    Column("setter_id", ForeignKey("setter.id"), primary_key=True),
)


class Boulder(Base):
    __tablename__ = "boulder"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id"))
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    url: Mapped[str] = mapped_column(String)
    number_of_repetitions: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    grade: Mapped["models.grade.Grade"] = relationship(
        "Grade", back_populates="boulders"
    )
    area: Mapped["models.area.Area"] = relationship(
        "Area", back_populates="boulders"
    )
    styles: Mapped[List["Style"]] = relationship(
        secondary=boulder_style_table, back_populates="boulders"
    )
    setters: Mapped[List["Setter"]] = relationship(
        secondary=boulder_setter_table, back_populates="boulders"
    )


class Style(Base):
    __tablename__ = "style"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    style: Mapped[str] = mapped_column(String)

    # Relationship
    boulders: Mapped[List["Boulder"]] = relationship(
        secondary=boulder_style_table, back_populates="styles"
    )

class Setter(Base):
    __tablename__ = "setter"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    setter: Mapped[str] = mapped_column(String)

    # Relationship
    boulders: Mapped[List["Boulder"]] = relationship(
        secondary=boulder_setter_table, back_populates="setters"
    )
