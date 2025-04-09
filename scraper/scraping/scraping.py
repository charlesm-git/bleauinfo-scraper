import asyncio
import re
import random
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError

from shared.models.boulder import Boulder, Repetition, Style, User
from shared.models.area import Area
from shared.models.grade import Grade
from shared.models.region import Region

BASE_URL = "https://bleau.info/"


async def get_areas(session, db_session):
    relative_area_list_url = "/areas_by_region"
    soup = await fetch(session, relative_area_list_url)

    # Get each region row
    regions_rows = soup.find_all("div", class_="area_by_regions")

    # For each region row, isolate each region
    for regions_row in regions_rows:
        regions_div = regions_row.find_all("div", class_="bi-col-3 col-top")
        # For each region, Create a region object and scrape all areas.
        for region_item in regions_div:
            region_name = region_item.find("strong").get_text()

            region = Region(name=region_name)
            db_session.add(region)
            db_session.commit()

            areas_div = region_item.find_all("div")
            for div in areas_div:
                # Find the first occurrence of an 'a' tag
                area = div.find("a")
                if not area:
                    continue

                # Extract useful data
                area_url = area.get("href")
                name = area.get_text().strip()
                status = None
                match = re.match(r"(.+)\s\((.*?)\)", name)
                if match:
                    name = match.group(1)
                    status = match.group(2)

                # Create the Area object
                area = Area(
                    name=name,
                    region_id=region.id,
                    url=area_url,
                    status=status,
                )
                db_session.add(area)
    db_session.commit()


async def scrap_all(session, db_session):
    areas = db_session.query(Area).all()
    for area in areas:
        await area_scraping(
            area_url=area.url,
            area_id=area.id,
            db_session=db_session,
            session=session,
        )
    # tasks = [
    #     area_scraping(
    #         area_url=area.url,
    #         area_id=area.id,
    #         db_session=db_session,
    #         session=session,
    #     )
    #     for area in areas
    # ]
    # await asyncio.gather(*tasks)


async def area_scraping(session, area_url, area_id, db_session):
    soup = await fetch(session, area_url)
    boulders = soup.find_all("div", class_="vsr")

    boulder_urls = [boulder.find("a").get("href") for boulder in boulders]

    tasks = [
        boulder_scraping(
            session=session,
            db_session=db_session,
            boulder_relative_url=boulder_url,
            area_id=area_id,
        )
        for boulder_url in boulder_urls
    ]
    await asyncio.gather(*tasks)


def styles_existance_check(style, db_session):
    """Check the existance of a style in the database from a name.
    If it doesn't exist, adds it.
    return: a Style instance"""
    style_object = db_session.query(Style).where(Style.style == style).first()
    if style_object:
        return style_object

    style_object = Style(style=style)
    db_session.add(style_object)
    db_session.flush()
    # db_session.refresh(style_object)
    return style_object


def user_existance_check(user, db_session):
    """Check the existance of a user in the database from a username.
    If it doesn't exist, adds it.
    return: a User instance"""
    user_object = db_session.query(User).where(User.url == user["url"]).first()
    if user_object:
        return user_object

    user_object = User(username=user["username"], url=user["url"])
    db_session.add(user_object)
    db_session.flush()
    # db_session.refresh(user_object)
    return user_object


async def boulder_scraping(session, db_session, boulder_relative_url, area_id):
    """Fetch boulder's data from a boulder page"""
    url = urljoin(BASE_URL, boulder_relative_url)

    soup = await fetch(session, boulder_relative_url)
    print(url)

    title = soup.find("h3")
    # From the header, extract the name and the grade
    name = list(title.children)[0].strip()
    print(name)
    grade = list(title.find("em").children)[0].get_text().strip()
    grade_id = Grade.get_id_from_value(
        db_session=db_session, grade_value=grade
    )

    slash_grade_id = None
    slash_grade = title.find("span", class_="ag")
    if slash_grade:
        slash_grade = slash_grade.get_text().strip()
        slash_grade_id = Grade.get_id_from_value(
            db_session=db_session, grade_value=slash_grade
        )

    # Get the styles
    styles = None
    scraped_styles = soup.find("div", class_="btype").get_text().strip()
    if scraped_styles != "-":
        styles = scraped_styles

    # Get the setters
    setters = None
    scraped_setters = (
        soup.find("div", class_="row bhead")
        .find("div", class_="col-md-12")
        .find("div")
        .find_all("a")
    )
    if scraped_setters is not None:
        setters = [
            {"username": setter.get_text().strip(), "url": setter.get("href")}
            for setter in scraped_setters
        ]

    # Initialise the rating and the number of repetition to default values
    rating = None
    number_of_rating = 0

    # Lookup for the section containing the rating and repetitions
    first_bopins = soup.find("div", class_="bdetails").find(
        "div", class_="bopins"
    )

    if first_bopins:
        title = first_bopins.find("strong").get_text()
        if title in ["Appréciation", "Average rating"]:
            rating = first_bopins.find_all("li")[2]
            rating = rating.get_text().strip().split(" ")[0].replace(",", ".")
            number_of_rating = first_bopins.find_all("li")[3]
            number_of_rating = number_of_rating.get_text().strip()
            match = re.match(r"\((\d+).*", number_of_rating)
            number_of_rating = int(match.group(1))

    # Create the boulder instance based on non nullable parameters
    boulder = Boulder(
        name=name,
        grade_id=grade_id,
        slash_grade_id=slash_grade_id,
        area_id=area_id,
        url=url,
        rating=rating,
        number_of_rating=number_of_rating,
    )
    db_session.add(boulder)
    db_session.commit()
    # Update the styles in the database
    if styles:
        styles = styles.split(",")
        styles = [style.strip() for style in styles]
        # Convert styles names into style objects
        for style in styles:
            try:
                with db_session.begin_nested():
                    style = styles_existance_check(
                        style=style, db_session=db_session
                    )
                    boulder.styles.append(style)
            except IntegrityError:
                print(f"Style '{style}' duplicated - skipped")
    # Update the setters in the database
    if setters:
        for setter in setters:
            # Convert username into User object
            setter = user_existance_check(user=setter, db_session=db_session)
            boulder.setters.append(setter)
            db_session.flush()
    # Scrape and save in the database all the repetition logged
    repetitions = soup.find_all("div", class_="repetition")

    for repetition in repetitions:
        children = list(repetition.children)

        # Extract the date of the repetition
        log_date = children[0]
        day, month, year = log_date.split("-")
        year = year.strip().replace(":", "")
        log_date = date(int(year), int(month), int(day))

        # Extract the name of the repetitor
        repetitor = {
            "username": children[1].get_text().strip(),
            "url": children[1].get("href"),
        }
        repetitor = user_existance_check(user=repetitor, db_session=db_session)

        try:
            with db_session.begin_nested():
                repetition = Repetition(
                    boulder_id=boulder.id,
                    user_id=repetitor.id,
                    log_date=log_date,
                )
                db_session.add(repetition)
        except IntegrityError:
            print(
                f"Skipped repetition by {repetitor['username']} on {log_date}"
            )

    db_session.commit()


semaphore = asyncio.Semaphore(20)

USER_AGENTS = [
    # Chrome - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.123 Safari/537.36",
    # Chrome - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox - Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    # Safari - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    # Safari - iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Edge - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.123 Safari/537.36 OPR/95.0.4635.84",
    # Android Chrome
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    # Samsung Internet
    "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/120.0.0.0 Mobile Safari/537.36",
    # Brave Browser (based on Chrome)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.199 Safari/537.36 Brave/1.62.162",
    # Vivaldi
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.199 Safari/537.36 Vivaldi/6.6.3271.61",
]

ACCEPTS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xml;q=0.9,*/*;q=0.8",
    "application/json, text/plain, */*",
    "text/html,application/xhtml+xml",
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "en-GB,en;q=0.9",
    "es-ES,es;q=0.9,en;q=0.8",
]

CONNECTIONS = ["keep-alive", "close"]


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice(ACCEPTS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Connection": random.choice(CONNECTIONS),
        "DNT": random.choice(["1", "0"]),
        "Upgrade-Insecure-Requests": random.choice(["1", "0"]),
    }


async def fetch(session, relative_url):
    url = urljoin(BASE_URL, relative_url)
    async with semaphore:
        # headers = get_random_headers()
        async with session.get(url) as response:
            html = await response.text()
            await asyncio.sleep(0.5)
            return BeautifulSoup(html, "html.parser")
