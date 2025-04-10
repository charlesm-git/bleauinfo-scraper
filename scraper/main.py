from time import time

import aiohttp
from scraper.analytics.analytics import get_average_grade, get_number_per_grade
from shared.database import Session, drop_tables, initialize_empty_db
from shared.models.boulder import Boulder, Repetition, Style, User
from shared.models.grade import Grade
from scraper.scraping.area_scraping import (
    scrape_boulders_from_area,
    boulder_scraping,
    scrape_regions,
    scrape_all_areas,
)
from shared.models.boulder import boulder_setter_table, boulder_style_table


async def scraper_main():
    drop_tables()
    initialize_empty_db()
    start = time()
    with Session() as db:
        async with aiohttp.ClientSession() as session:
            await scrape_regions(session=session, db=db)
            await scrape_all_areas(session=session, db=db)
            # await area_scraping(
            #     session=session,
            #     area_id=2,
            #     area_url="/cuvier",
            #     db=db,
            # )
            # await boulder_scraping(
            #     session=session,
            #     db=db,
            #     boulder_relative_url="/cul/173.html",
            #     area_id=1,
            # )

            # query = (
            #     db.query(
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
            # query = db.scalars(select(Boulder))
            # for boulder in query:
            #     print(boulder)
            # print(boulder.id)
            # print(get_number_per_grade(db=db))
            # print(get_average_grade(db=db))
    end = time()

    print(f"Execution time: {end - start:.4f} seconds")
