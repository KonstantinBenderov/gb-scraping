import json

import requests
from bs4 import BeautifulSoup

position = input('Введите название должности для поиска (по умолчанию - Python Developer): ')
if not position:
    position = 'Python Developer'

params = {
    'text': position,
    'page': 0
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

domain = 'https://hh.ru'
url = domain + '/search/vacancy'
session = requests.Session()

vacancies_list = []
counter = 0

while True:
    print(f'\rpage {params["page"]+1}', end='')
    response = session.get(url, params=params, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')
    vacancies = bs.select('.vacancy-serp-item__layout')

    for vacancy in vacancies:
        vacancy_data = {}
        employer = {
            'name': vacancy.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0].text.replace('\xa0', ' '),
            'link': domain + vacancy.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0]['href'].split('?')[0]
        }
        title = vacancy.select('a[data-qa="vacancy-serp__vacancy-title"]')[0]
        title_text = title.text
        title_href = title['href'].split('?')[0]
        salary = vacancy.select('span[data-qa="vacancy-serp__vacancy-compensation"]')
        if salary:
            salary = salary[0].text.replace('\u202f', '').replace(' – ', ' ').split(' ')
            try:
                salary[0] = int(salary[0])
            except Exception:
                salary[0] = None
            try:
                salary[1] = int(salary[1])
            except Exception:
                salary[1] = None

        else:
            salary = None
        vacancy_data['employer'] = employer
        vacancy_data['title'] = title_text
        vacancy_data['salary'] = salary
        vacancy_data['href'] = title_href
        vacancy_data['site'] = domain
        vacancies_list.append(vacancy_data)
        counter += 1

    next_button = bs.select('a[data-qa="pager-next"]')
    if next_button:
        params['page'] += 1
    else:
        file = 'vacancies.json'
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(vacancies_list, f, indent=4, ensure_ascii=False)
        print(f'\n{counter} vacancies => {file} ')
        break
