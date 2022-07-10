from pprint import pprint

from pymongo import MongoClient


def filter_by_salary(vacancies, payment: int) -> list:
    return list(vacancies.find(
        {'$or': [
            {'salary_min': {'$gt': payment}},
            {'salary_max': {'$lt': payment}}]
        }))


if __name__ == '__main__':
    client = MongoClient('127.0.0.1', 27017)
    db = client['gb-scraping']
    db_vacancies = db.vacancies
    pprint(filter_by_salary(db_vacancies, 50000))
