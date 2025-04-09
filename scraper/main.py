import asyncio
from time import time

import aiohttp
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import aliased
from scraper.analytics.analytics import get_average_grade, get_number_per_grade
from shared.database import Session, drop_tables, initialize_empty_db
from shared.models.boulder import Boulder, Repetition, Style, User
from shared.models.grade import Grade
from scraper.scraping.scraping import (
    area_scraping,
    boulder_scraping,
    get_areas,
    scrap_all,
)
from shared.models.boulder import boulder_setter_table, boulder_style_table


async def scraper_main():
    drop_tables()
    initialize_empty_db()
    start = time()
    with Session() as db_session:
        async with aiohttp.ClientSession() as session:
            await get_areas(session=session, db_session=db_session)
            await scrap_all(session=session, db_session=db_session)
            # await area_scraping(
            #     session=session,
            #     area_id=2,
            #     area_url="/cuvier",
            #     db_session=db_session,
            # )
            # await boulder_scraping(
            #     session=session,
            #     db_session=db_session,
            #     boulder_relative_url="/cul/173.html",
            #     area_id=1,
            # )

            # query = (
            #     db_session.query(
            #         Boulder.name,
            #         Grade.value,
            #         Boulder.rating,
            #     )
            #     .join(Grade, Boulder.grade_id == Grade.id)
            #     .filter(
            #         Grade.correspondence == 21, Boulder.number_of_rating > 7
            #     )
            #     .order_by(desc(Boulder.rating))
            #     .limit(10)
            #     .all()
            # )
            # query = db_session.scalars(select(Boulder))
            # for boulder in query:
            #     print(boulder)
            # print(boulder.id)$
            # print(get_number_per_grade(db_session=db_session))
            # print(get_average_grade(db_session=db_session))
    end = time()

    print(f"Execution time: {end - start:.4f} seconds")
