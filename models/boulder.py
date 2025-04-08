from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, Table, Column, Float, Integer, String, ForeignKey

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
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)


class Boulder(Base):
    __tablename__ = "boulder"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id"))
    slash_grade_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("grade.id"), nullable=True, default=None
    )
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    number_of_rating: Mapped[int] = mapped_column(Integer, default=0)
    url: Mapped[str] = mapped_column(String, unique=True)

    # Relationship to other entities via Foreign Keys
    grade: Mapped["models.grade.Grade"] = relationship(
        "Grade", back_populates="boulders", foreign_keys=[grade_id]
    )
    slash_grade: Mapped[Optional["models.grade.Grade"]] = relationship(
        "Grade", foreign_keys=[slash_grade_id]
    )
    area: Mapped["models.area.Area"] = relationship(
        "Area", back_populates="boulders"
    )

    # Many-to-Many relationship to styles and setters using core tables
    styles: Mapped[List["Style"]] = relationship(
        secondary=boulder_style_table, back_populates="boulders"
    )
    setters: Mapped[List["User"]] = relationship(
        secondary=boulder_setter_table, back_populates="set_boulders"
    )

    # Association object for repetitions
    repetitions: Mapped[List["Repetition"]] = relationship(
        "Repetition", back_populates="boulder"
    )

    def __repr__(self):
        return f"<Boulder(name: {self.name}, grade: {self.grade.value}, setters: {self.setters}, repetitions: {self.repetitions})"


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


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, unique=True)

    # Relationship
    set_boulders: Mapped[List["Boulder"]] = relationship(
        secondary=boulder_setter_table, back_populates="setters"
    )
    repetitions: Mapped[List["Repetition"]] = relationship(
        "Repetition", back_populates="user"
    )

    def __repr__(self):
        return f"<User(id: {self.id}, username: {self.username})>"


class Repetition(Base):
    __tablename__ = "boulder_repetition"

    boulder_id: Mapped[int] = mapped_column(
        ForeignKey("boulder.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    log_date: Mapped[date] = mapped_column(Date)

    boulder: Mapped["Boulder"] = relationship(
        "Boulder", back_populates="repetitions"
    )
    user: Mapped["User"] = relationship("User", back_populates="repetitions")

    def __repr__(self):
        return f"<Repetition({self.user})"
