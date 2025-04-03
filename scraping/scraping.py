import re
from time import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import GRADE_ASSOCIATION_DICT, Session
from models.boulder import Boulder, Style, Setter
from models.area import Area
from models.region import Region

BASE_URL = "https://bleau.info/"


def get_areas():
    with Session() as session:
        relative_area_url = "/areas_by_region"
        areas_list_url = urljoin(BASE_URL, relative_area_url)

        response = requests.get(areas_list_url)        
        soup = BeautifulSoup(response.content, "html.parser")

        # Get each region row
        regions_rows = soup.find_all("div", class_="area_by_regions")

        regions = []

        # For each region row, isolate each region
        for regions_row in regions_rows:
            regions_div = regions_row.find_all(
                "div", class_="bi-col-3 col-top"
            )
            # For each region, Create a region object and scrape all areas.
            for region_item in regions_div:
                region_name = region_item.find("strong").get_text()

                region = Region(name=region_name)
                session.add(region)
                session.commit()

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
                    session.add(area)
        session.commit()


def get_boulders():
    with Session() as session:
        urls = session.query(Area.url, Area.id).all()
        print(urls)


def area_scraping(area_url, area_id):
    with Session() as session:
        url = urljoin(BASE_URL, area_url)

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        boulders = soup.find_all("div", class_="vsr")

        for boulder in boulders:
            a_tag = boulder.find("a")

            url = a_tag.get("href")
            name = a_tag.get_text().strip()
            grade = a_tag.next_sibling.text.strip()
            grade_id = GRADE_ASSOCIATION_DICT.get(grade)

            styles = None
            if boulder.find("span", class_="btype") is not None:
                styles = boulder.find("span", class_="btype").get_text()

            setters = None
            if boulder.find("em") is not None:
                setters = boulder.find("em").get_text()

            rating, number_of_repetitions = boulder_additional_details(url)

            boulder = Boulder(
                name=name,
                grade_id=grade_id,
                area_id=area_id,
                url=url,
                rating=rating,
                number_of_repetitions=number_of_repetitions,
            )
            session.add(boulder)

            if styles:
                styles = styles.split(",")
                styles = [style.strip() for style in styles]
                # Convert styles names into style objects
                styles = styles_existance_check(styles=styles, session=session)
                for style in styles:
                    boulder.styles.append(style)
            if setters:
                setters = setters.split(",")
                setters = [setter.strip() for setter in setters]
                setters = setters_existance_check(
                    setters=setters, session=session
                )
                for setter in setters:
                    boulder.setters.append(setter)

        session.commit()


def styles_existance_check(styles, session):
    """Check the existance of a list of styles in the database.
    All non existing styles are added"""
    style_objects = []
    for style in styles:
        existing_style = (
            session.query(Style).where(Style.style == style).first()
        )
        if existing_style:
            style_objects.append(existing_style)
            continue

        existing_style = Style(style=style)
        session.add(existing_style)
        session.commit()
        session.refresh(existing_style)
        style_objects.append(existing_style)
    return style_objects


def setters_existance_check(setters, session):
    """Check the existance of a list of setters in the database.
    All non existing setters are added"""
    setter_objects = []
    for setter in setters:
        existing_setter = (
            session.query(Setter).where(Setter.setter == setter).first()
        )
        if existing_setter:
            setter_objects.append(existing_setter)
            continue

        existing_setter = Setter(setter=setter)
        session.add(existing_setter)
        session.commit()
        session.refresh(existing_setter)
        setter_objects.append(existing_setter)
    return setter_objects


def boulder_additional_details(boulder_relative_url):
    """
    Fetch additional details on a boulder's page
    :return: the exact rating and the number of repetitions
    """
    url = urljoin(BASE_URL, boulder_relative_url)

    rating = None
    number_of_repetition = 0

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    bopins = soup.find_all("div", class_="bopins")

    if not bopins:
        return rating, number_of_repetition

    for bopin in bopins:
        title = bopin.find("strong").get_text()
        match (title):
            case "Appréciation":
                rating = bopin.find_all("li")[2]
                rating = (
                    rating.get_text().strip().split(" ")[0].replace(",", ".")
                )
            case "Répétitions publiques":
                number_of_repetition = bopin.find_all("li")[2]
                number_of_repetition = number_of_repetition.get_text().strip()
                match = re.match(r"\((\d+).*", number_of_repetition)
                number_of_repetition = int(match.group(1))
    return rating, number_of_repetition
