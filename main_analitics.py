from database import get_full_database
from analytics.analytics import (
    get_average_grade,
    get_number_of_boulders_above_7a,
    get_number_per_grade,
    get_pourcentage_per_grade,
)

database = get_full_database()
number_of_boulders = len(database)
number_above_7a = get_number_of_boulders_above_7a(database)
number_per_grade = get_number_per_grade(database)
pourcentage_per_grade = get_pourcentage_per_grade(database)
average_grade = get_average_grade(database)

print("Number of boulders:", number_of_boulders)
print("Number above 7a:", number_above_7a)
print("Number per grade:", number_per_grade)
print("Poucentage per grade:", pourcentage_per_grade)
print("Average grade:", average_grade)
