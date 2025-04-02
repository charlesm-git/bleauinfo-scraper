import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from models.boulder import Boulder
from models.area import Area
from models.region import Region

BASE_URL = "https://bleau.info/"


def get_regions():
    relative_area_url = "/areas_by_region"
    areas_list_url = urljoin(BASE_URL, relative_area_url)

    response = requests.get(areas_list_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get each region row
    regions_rows = soup.find_all("div", class_="area_by_regions")

    regions = []

    # For each region row, isolate each region
    for regions_row in regions_rows:
        regions_div = regions_row.find_all("div", class_="bi-col-3 col-top")
        # For each region, Create a region object and scrape all areas.
        for region_item in regions_div:
            region_name = region_item.find("strong").get_text()
            region = Region(name=region_name)

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
                    name=name, region=region, url=area_url, status=status
                )
                # Append the area created to the region
                region.areas.append(area)
            regions.append(region)
    return regions


def area_scraping(area):
    url = urljoin(BASE_URL, area.url)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    boulders = soup.find_all("div", class_="vsr")

    for boulder in boulders:
        a_tag = boulder.find("a")
        
        url = a_tag.get("href")
        name = a_tag.get_text().strip()
        grade = a_tag.next_sibling.text.strip()

        style = None
        if boulder.find("span", class_="btype") is not None:
            style = boulder.find("span", class_="btype").get_text()

        setter = None
        if boulder.find("em") is not None:
            setter = boulder.find("em").get_text()

        rating, number_of_repetitions = boulder_additional_details(url)

        area.boulders.append(
            Boulder(
                name=name,
                grade=grade,
                area=area,
                url=url,
                setter=setter,
                number_of_repetitions=number_of_repetitions,
                rating=rating,
                style=style,
            )
        )

def boulder_additional_details(boulder_relative_url):
    url = urljoin(BASE_URL, boulder_relative_url)
    
    rating = None
    number_of_repetition = 0
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    bopins = soup.find_all("div", class_="bopins")
    
    if not bopins:
        return rating, number_of_repetition
    
    for bopin in bopins:
        title = bopin.find('strong').get_text()
        match(title):
            case("Appréciation"):
                rating = bopin.find_all("li")[2]
                rating = rating.get_text().strip().split(" ")[0]
            case("Répétitions publiques"):
                number_of_repetition = bopin.find_all("li")[2]
                number_of_repetition = number_of_repetition.get_text().strip()
                match = re.match(r"\((\d+).*", number_of_repetition)
                number_of_repetition = match.group(1)
    return rating, number_of_repetition
