# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и
#    реализовать функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии
#    с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты).
#    То есть цифра вводится одна, а запрос проверяет оба поля
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['gb-scraping']
db_vacancies = db.vacancies

position = input('Введите название должности для поиска (по умолчанию - Python Developer): ')
if not position:
    position = 'Python Developer'

params = {
    'text': position,
    'page': 0,
    'items_on_page': 20
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

domain = 'https://hh.ru'
url = domain + '/search/vacancy'
session = requests.Session()

counter = 0
new_vacancies = 0
old_vacancies = 0
error = 0
while True:
    print(f'\rpage {params["page"] + 1}', end='')
    response = session.get(url, params=params, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')
    vacancies = bs.select('.vacancy-serp-item__layout')

    for vacancy in vacancies:
        try:
            vacancy_data = {}
            employer = {
                'name': vacancy.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0].text.replace('\xa0', ' '),
                'link': domain + vacancy.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0]['href'].split('?')[0]
            }
            title = vacancy.select('a[data-qa="vacancy-serp__vacancy-title"]')[0]
            title_text = title.text
            title_href = title['href'] if '/click?' in title['href'] else title['href'].split('?')[0]
            salary = vacancy.select('span[data-qa="vacancy-serp__vacancy-compensation"]')
            if salary:
                salary = salary[0].text.replace('\u202f', '').replace(' – ', ' ').split(' ')
                try:
                    vacancy_data['salary_min'] = int(salary[0])
                except Exception:
                    vacancy_data['salary_min'] = None
                try:
                    vacancy_data['salary_max'] = int(salary[1])
                    vacancy_data['currency'] = salary[2]
                except Exception:
                    vacancy_data['salary_max'] = None
        except Exception as err:
            print('\n### Bad selector? Error:', err)
            error += 1
            continue

        _id = title_href.split('/')[-1]
        vacancy_data['request'] = position.lower()
        vacancy_data['_id'] = _id
        vacancy_data['employer'] = employer
        vacancy_data['title'] = title_text
        # vacancy_data['salary'] = salary
        vacancy_data['href'] = title_href
        vacancy_data['site'] = domain

        has_vacancy = bool(db_vacancies.find_one({'_id': _id}))
        if has_vacancy:
            old_vacancies += 1
            db_vacancies.update_one({'_id': _id}, {'$set': vacancy_data})
        else:
            vacancy_data['scraped_at'] = datetime.now()
            new_vacancies += 1
            db_vacancies.insert_one(vacancy_data)

        counter += 1

    next_button = bs.select('a[data-qa="pager-next"]')
    if next_button:
        params['page'] += 1
    else:
        print(f'\n\nTotal: {counter} vacancies')
        print(f'New vacancies: {new_vacancies}')
        print(f'Old vacancies: {old_vacancies}')
        print(f'Errors of scrapping: {error}')
        exit(1)
