from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base import Base
from models.area import Area
from models.grade import Grade

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

db_path = "bleau_info.db"

DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False)

session_factory = sessionmaker(bind=engine)

Session = scoped_session(session_factory)


def get_grades_as_object():
    """
    Create and return a list of Grade Objects to initialize the 'grade' table
    in the database
    """
    grades = []
    for value, correspondence in GRADE_ASSOCIATION_DICT.items():
        grades.append(
            Grade(value=value, correspondence=correspondence)
        )
    return grades


def initialize_empty_db():
    grades = get_grades_as_object()
    with Session() as session:
        Base.metadata.create_all(engine)
        session.add_all(grades)
        session.commit()

def drop_tables():
    Base.metadata.drop_all(engine)