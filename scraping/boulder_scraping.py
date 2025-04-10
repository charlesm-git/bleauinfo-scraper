import re
from datetime import date
from urllib.parse import urljoin

from sqlalchemy.exc import IntegrityError

from scraping.fetch import fetch, BASE_URL
from models.boulder import Boulder
from models.style import Style
from models.user import User
from models.repetition import Repetition
from models.grade import Grade


async def boulder_scraping(session, db, boulder_relative_url, area_id):
    """Fetch boulder's data from a boulder page"""
    url = urljoin(BASE_URL, boulder_relative_url)

    soup = await fetch(session, boulder_relative_url)
    print(url)

    title = soup.find("h3")
    # Extract the name and the grade from the header
    name = list(title.children)[0].strip()
    print(name)
    grade = list(title.find("em").children)[0].get_text().strip()
    grade_id = Grade.get_id_from_value(db=db, grade_value=grade)

    # Extract slash grade
    slash_grade_id = None
    slash_grade = title.find("span", class_="ag")
    if slash_grade:
        slash_grade = slash_grade.get_text().strip()
        slash_grade_id = Grade.get_id_from_value(
            db=db, grade_value=slash_grade
        )

    # Extract styles
    styles = None
    scraped_styles = soup.find("div", class_="btype").get_text().strip()
    if scraped_styles != "-":
        styles = scraped_styles

    # Extract setters
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

    # If any, extract the rating andd the number of rating
    first_bopins = soup.find("div", class_="bdetails").find(
        "div", class_="bopins"
    )
    if first_bopins:
        title = first_bopins.find("strong").get_text()
        if title in ["Appréciation", "Average rating"]:
            # Rating extraction
            rating = first_bopins.find_all("li")[2]
            rating = rating.get_text().strip().split(" ")[0].replace(",", ".")
            # Number of rating extraction
            number_of_rating = first_bopins.find_all("li")[3]
            number_of_rating = number_of_rating.get_text().strip()
            match = re.match(r"\((\d+).*", number_of_rating)
            number_of_rating = int(match.group(1))

    # Create the boulder instance based on non nullable parameters
    boulder = Boulder.create(
        db=db,
        name=name,
        grade_id=grade_id,
        slash_grade_id=slash_grade_id,
        area_id=area_id,
        url=url,
        rating=rating,
        number_of_rating=number_of_rating,
    )

    # Update the styles in the database
    if styles:
        styles = styles.split(",")
        styles = [style.strip() for style in styles]
        # Convert styles names into style objects
        for style in styles:
            try:
                with db.begin_nested():
                    style = styles_existance_check(style=style, db=db)
                    boulder.styles.append(style)
            except IntegrityError:
                print(f"Style '{style}' duplicated - skipped")

    # Update the setters in the database
    if setters:
        # Convert username into User object
        for setter in setters:
            try:
                with db.begin_nested():
                    setter = user_existance_check(user=setter, db=db)
                    boulder.setters.append(setter)
            except IntegrityError:
                print(f"Setter '{setter}' duplicated - skipped")

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
        repetitor = user_existance_check(user=repetitor, db=db)

        try:
            with db.begin_nested():
                repetition = Repetition(
                    boulder_id=boulder.id,
                    user_id=repetitor.id,
                    log_date=log_date,
                )
                db.add(repetition)
        except IntegrityError:
            print(
                f"Skipped repetition by {repetitor['username']} on {log_date}"
            )
    db.commit()


def styles_existance_check(style, db):
    """Check the existance of a style in the database from a name.
    If it doesn't exist, adds it.
    return: a Style instance"""
    style_object = db.query(Style).where(Style.style == style).first()
    if style_object:
        return style_object

    style_object = Style(style=style)
    db.add(style_object)
    db.flush()
    return style_object


def user_existance_check(user, db):
    """Check the existance of a user in the database from a username.
    If it doesn't exist, adds it.
    return: a User instance"""
    user_object = db.query(User).where(User.url == user["url"]).first()
    if user_object:
        return user_object

    user_object = User(username=user["username"], url=user["url"])
    db.add(user_object)
    db.flush()
    return user_object
