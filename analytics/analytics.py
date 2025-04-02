GRADE_ASSOCIATION_DICT = {
    "1": 1,
    "2": 2,
    "2+": 3,
    "3-": 4,
    "3": 5,
    "3+": 6,
    "4-": 7,
    "4": 8,
    "4+": 9,
    "5-": 10,
    "5": 11,
    "5+": 12,
    "6a": 13,
    "6a+": 14,
    "6b": 15,
    "6b+": 16,
    "6c": 17,
    "6c+": 18,
    "7a": 19,
    "7a+": 20,
    "7b": 21,
    "7b+": 22,
    "7c": 23,
    "7c+": 24,
    "8a": 25,
    "8a+": 26,
    "8b": 27,
    "8b+": 28,
    "8c": 29,
    "8c+": 30,
    "9a": 31,
    "P": 32,
}


def get_grade_correspondance(grade):
    return GRADE_ASSOCIATION_DICT.get(grade, 0)


def get_number_of_boulders_above_7a(boulders_database):
    grade_7a = get_grade_correspondance("7a")
    counter = 0
    for boulder in boulders_database:
        if get_grade_correspondance(boulder.grade) >= grade_7a:
            counter += 1
    return counter


# def get_number_per_area(boulders_database):
#     number_per_area = {}
#     for boulder in boulders_data:
#         if boulder["area"] not in number_per_area:
#             number_per_area[boulder["area"]] = 0
#         number_per_area[boulder["area"]] += 1
#     return number_per_area


# def get_pourcentage_per_area(boulders_database):
#     number_per_area = get_number_per_area(boulders_data)
#     total_boulder = len(boulders_data)
#     pourcentage_per_area = {}
#     for area in number_per_area:
#         pourcentage_per_area[area] = round(
#             number_per_area[area] / total_boulder * 100, 1
#         )
#     return pourcentage_per_area


def get_number_per_grade(boulders_database):
    number_per_grade = {}
    for boulder in boulders_database:
        if boulder.grade not in number_per_grade:
            number_per_grade[boulder.grade] = 0
        number_per_grade[boulder.grade] += 1
    sorted_dict = dict(sorted(number_per_grade.items()))
    return sorted_dict


def get_pourcentage_per_grade(boulders_database):
    number_per_grade = get_number_per_grade(boulders_database)
    total_boulder = len(boulders_database)
    pourcentage_per_grade = {}
    for grade in number_per_grade:
        pourcentage_per_grade[grade] = round(
            number_per_grade[grade] / total_boulder * 100, 2
        )
    return pourcentage_per_grade


def get_average_grade(boulders_database):
    grade_sum = 0
    for boulder in boulders_database:
        correspondance = get_grade_correspondance(boulder.grade)
        grade_sum += correspondance
    average_correspondance_grade = round(grade_sum / len(boulders_database))
    average_grade = 0
    for key, val in GRADE_ASSOCIATION_DICT.items():
        if val == average_correspondance_grade:
            average_grade = key
    return average_grade
