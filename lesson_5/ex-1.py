# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и
# сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#
from time import sleep

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Wait

# Settings
client = MongoClient('127.0.0.1', 27017)
db = client['gb-scraping']
db_mail = db.mail

login = 'study.ai_172@mail.ru'
password = 'NextPassword172#'

service = Service('drivers/geckodriver.exe')
options = Options()

driver = webdriver.Firefox(service=service)
actions = webdriver.ActionChains(driver)

driver.get('https://mail.ru')

# Log in mail.ru
enter_btn = driver.find_element(By.XPATH, "//button[@data-testid='enter-mail-primary']")
enter_btn.click()

# Switch to login form frame
login_frame = Wait(driver, 30).until(
    EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@class='ag-popup__frame__layout__iframe']"))
)

login_input = Wait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
)

login_input.clear()
login_input.send_keys(login, Keys.ENTER)

password_input = Wait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
)
sleep(1)
password_input.clear()
password_input.send_keys(password, Keys.ENTER)

# Switch back to main frame
driver.switch_to.default_content()

inbox = Wait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="ReactVirtualized__Grid__innerScrollContainer"]'))
)

# Get total incoming mail
letters_total = int(driver.find_element(By.XPATH, '//a[@href="/inbox/"]').get_attribute('title').split(' ')[1])
print()

# Click to focus on the required element
up = driver.find_element(By.XPATH, '//span[@class="paginator-container__block"]')
target = {'x': up.location['x'] + int(up.size['height'] + 5), 'y': up.location['y'] + int(up.size['width'] + 5)}
actions.move_by_offset(target['x'], target['y']).perform()

# Collecting letters id
letters_id = []
print('Collecting letters id...')
while True:
    for item in inbox.find_elements(By.XPATH, './a'):
        _id = item.get_attribute('data-uidl-id')
        if _id not in letters_id:
            letter_from_db = db_mail.find_one({'_id': _id})
            _has_letter = bool(letter_from_db)
            if _has_letter:
                if 'Сегодня' or 'Вчера' in letter_from_db['date']:
                    _date = item.find_element(By.XPATH, './/div[@title]').get_attribute('title')
                    letter_from_db['date'] = _date
                else:
                    break
            else:
                letters_id.append(_id)

    actions.click().perform()
    actions.send_keys(Keys.PAGE_DOWN).perform()
    sleep(2)

    # # Break when all collected
    # if len(letters_id) == letters_total:
    #     break

    # Test break (
    if len(letters_id) >= 10:
        break


print(f'New letters: {len(letters_id)}\n')
print('Getting letters by id...\n')

# Get letters by id
for i, _id in enumerate(letters_id):
    try:
        # If letter exists
        driver.get(f'https://e.mail.ru/inbox/0:{_id}:0')
        print(f'\rLetter {i + 1} of {len(letters_id)}', end='')
    except Exception:
        continue

    _content = Wait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="layout__letter-content"]'))
    )

    _letter = {}
    _date = _content.find_element(By.XPATH, './/div[@class="letter__date"]').text
    _letter['_id'] = _id
    _letter['sender'] = str(_content.find_element(By.XPATH, './/span[@class="letter-contact"]').text)
    _letter['email'] = str(_content.find_element(By.XPATH, './/span[@class="letter-contact"]').get_attribute('title'))
    _letter['date'] = str(_date)
    _letter['header'] = str(_content.find_element(By.XPATH, './/h2').text)
    _letter['content'] = _content.find_element(By.XPATH, f'.//div[@data-id="{_id}"]').get_attribute('innerHTML')

    db_mail.insert_one(_letter)

else:
    print(f'\n\nNew letters: {len(letters_id)}')
    print(f'      Total: {len(list(db_mail.find({})))} letters')
