from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from shared.models.base import Base
import shared.models.area


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String)

    # Relationship
    areas: Mapped[List["shared.models.area.Area"]] = relationship(
        back_populates="region"
    )

    def __repr__(self):
        return f"<Region(name: {self.name}, areas: {self.areas})>"
