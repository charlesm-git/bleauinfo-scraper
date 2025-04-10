from sqlalchemy import desc, func, or_, select

from models.boulder import Boulder
from models.style import Style
from models.boulder_style import boulder_style_table
from models.grade import Grade


def get_number_per_grade(db_session):
    sub_query = (
        select(boulder_style_table.c.boulder_id)
        .where(
            or_(
                Style.style == "traversée",
                Style.style == "traversée g-d",
                Style.style == "traversée d-g",
            )
        )
        .join(Style, Style.id == boulder_style_table.c.style_id)
    )

    query = db_session.execute(
        select(Grade.value, func.count(Boulder.id))
        .where(Boulder.id.not_in(sub_query))
        .join(Boulder, Grade.id == Boulder.grade_id)
        .group_by(Grade.value)
        .order_by(desc(Grade.correspondence))
    ).all()
    return query


def get_average_grade(db_session):
    average_correspondence = (
        select(func.avg(Grade.correspondence))
        .join(Boulder, Boulder.grade_id == Grade.id)
        .scalar_subquery()
    )

    query = db_session.scalar(
        select(Grade.value).where(
            Grade.correspondence == func.round(average_correspondence)
        )
    )
    return query
