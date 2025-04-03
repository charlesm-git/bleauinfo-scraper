from time import time
from database import drop_tables, initialize_empty_db
from scraping.scraping import area_scraping, get_areas, get_boulders


if __name__ == "__main__":
    
    drop_tables()
    initialize_empty_db()
    start = time()
    get_areas()
    # get_boulders()
    # area_scraping(area_url="/diable", area_id=141)
    end = time()
    
    print(f"Execution time: {end - start:.4f} seconds")