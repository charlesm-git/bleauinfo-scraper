import asyncio
from time import time

import aiohttp
from database import Session, drop_tables, initialize_empty_db
from scraping.area_scraping import (
    scrape_regions,
    scrape_all_areas,
    scrape_areas_from_region,
)
from scraping.boulder_scraping import boulder_scraping


async def main():
    drop_tables()
    initialize_empty_db()
    start = time()
    with Session() as db:
        async with aiohttp.ClientSession() as session:
            await scrape_regions(session=session, db=db)
            # await scrape_all_areas(session=session, db=db)
            # await scrape_areas_from_region(
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

if __name__ == "__main__":
    asyncio.run(main())