from unidecode import unidecode
import re
import csv


def clean_string(string):
    # Remove accents
    cleaned_string = unidecode(string)
    # Remove forbidden characters
    invalid_chars = r'<>:"/\\|?*\x00-\x1F'
    cleaned_string = re.sub(f"[{invalid_chars}]", "", cleaned_string)
    # Remove potential blank spaces before and after the string
    cleaned_string = cleaned_string.strip()
    # Replace the inner space by _
    cleaned_string = cleaned_string.replace(" ", "_")

    return cleaned_string


def save_area(area):
    file_name = clean_string(area.name)
    with open(
        f"./data/areas/{file_name}.csv",
        "w",
        encoding="utf-8",
        newline="",
    ) as area_file:
        writer = csv.writer(area_file, delimiter=";")
        for boulder in area.boulders:
            writer.writerow(boulder.as_list())
