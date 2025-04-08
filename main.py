import asyncio
from time import time

import aiohttp
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import aliased
from database import Session, drop_tables, initialize_empty_db
from models.boulder import Boulder, Repetition, Style, User
from models.grade import Grade
from scraping.scraping import (
    area_scraping,
    boulder_scraping,
    get_areas,
    scrap_all,
)
from models.boulder import boulder_setter_table, boulder_style_table


async def main():
    # drop_tables()
    # initialize_empty_db()
    start = time()
    with Session() as db_session:
        async with aiohttp.ClientSession() as session:
            # await get_areas(session=session, db_session=db_session)
            # await scrap_all(session=session, db_session=db_session)
            # await area_scraping(
            #     session=session,
            #     area_id=2,
            #     area_url="/cuvier",
            #     db_session=db_session,
            # )
            # await boulder_scraping(
            #     session=session,
            #     db_session=db_session,
            #     boulder_relative_url="/cuvier/1150.html",
            #     area_id=1,
            # )

            query = (
                db_session.query(
                    Boulder.name,
                    Grade.value,
                    func.count(Boulder.repetitions).label("rep_count"),
                )
                .join(Grade, Boulder.grade_id == Grade.id)
                .join(Repetition, Boulder.id == Repetition.boulder_id)
                .filter(Grade.correspondence == 25)
                .group_by(Repetition.boulder_id)
                .order_by(desc("rep_count"))
                .limit(10)
                .all()
            )
            for boulder in query:
                print(boulder)
    end = time()

    print(f"Execution time: {end - start:.4f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
