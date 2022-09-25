# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
from pprint import pprint
import csv
from pymongo import MongoClient, errors
import zlib
import re
import pymongo

def save_pickle(o, path):
    with open(path, 'wb') as f:
        pickle.dump(o, f)


def load_pickle(path):
    with open(path, 'rb') as f:
        data_new = pickle.load(f, encoding='utf-8')
        return data_new


load_dotenv()
path = "hh_part_1.csv"
EMAIL = os.getenv('EMAIL')  #
PASSWORD = os.getenv('PASSWORD')  #
DRIVER_PATH = './msedgedriver.exe'
driver = webdriver.Edge(DRIVER_PATH)
url = 'https://hh.ru/account/login?backurl=%2F'
driver.get(url)
search_name = 'обучение персонала'
client = pymongo.MongoClient()
db = client['hh_new_db']
collection = db['hhru']  # Выбираем коллекцию по имени паука


time.sleep(6)
user_email = driver.find_element_by_xpath('//div[contains(@class, "bloko-form-item")]/input')
user_email.send_keys(EMAIL)
time.sleep(5)
btn_pswd = driver.find_element_by_xpath('//div[contains(@class, "account-login-actions")]/span')
btn_pswd.click()
time.sleep(5)
user_password = driver.find_element_by_xpath('//div[contains(@class, "bloko-form-item")]/span[contains(@class, "bloko-input-wrapper")]/input')
user_password.send_keys(PASSWORD)
time.sleep(8)
btn = driver.find_element_by_xpath('//div[contains(@class, "account-login-actions")]/button')
btn.click()
time.sleep(60)
btn.click()
time.sleep(8)
url = f'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text={search_name}'
driver.get(url)
time.sleep(6)


page = 0

vacansion_hh = []
count = 0
while True:
    items = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-serp-item__info")]/span/span/span/a')
    i = 0
    for j in items:
        items = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-serp-item__info")]/span/span/span/a')
        info_hh = {}
        save_pickle(info_hh, path)
        items_2 = items

        # search and save
        if len(items) >= i:
            x = items_2[i]
            name_link = items_2[i].text
            link_vacansion = items_2[i].get_attribute('href')
            print(link_vacansion)
            driver.get(link_vacansion)
            time.sleep(7)

            employer = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-company__details")]')[0].text
            print(employer)
            time.sleep(5)
            href_employer = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-company__details")]/a')[0].get_attribute('href')
            time.sleep(8)
            try:
                btn_contacts = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-section")]/h2[contains(@class, "bloko-header-2")]/span')[0]
                btn_contacts.click()
                try:
                    name_HR = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-contacts__body")]/p[contains(@data-qa, "vacancy-contacts__fio")]/span')[0].text
                    print(name_HR)
                except IndexError:
                    name_HR = None
                time.sleep(8)
                try:
                    tel = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-contacts__phone-mobile")]/a')[0].get_attribute('href')
                except IndexError:
                    tel = None
                time.sleep(7)

                try:
                    email_HR = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-contacts__body")]/a')[0].text
                except IndexError:
                    email_HR = None
                time.sleep(7)

                try:
                    adress = driver.find_elements_by_xpath('//div[contains(@class, "vacancy-address-text")]/span')[0].text
                except IndexError:
                    adress = None
                time.sleep(7)
            except IndexError:
                name_HR = None
                adress = None
                email_HR = None
                tel = None

            count += 1
            info_hh['count'] = count
            info_hh['name'] = name_link
            info_hh['href'] = link_vacansion
            info_hh['employer'] = employer
            info_hh['name_HR'] = name_HR
            info_hh['tel'] = tel
            info_hh['adress'] = adress
            info_hh['href_employer'] = info_hh
            info_hh['website'] = 'https://www.hh.ru'
            vacansion_hh.append(info_hh)
            pprint(info_hh)
            load_pickle(path)
            time.sleep(5)
            driver.back()

            try:
                collection.insert_one(info_hh) # Добавляем в базу данных
            except errors.DuplicateKeyError:
                print("Duplicate found for vacancy: ", info_hh)
                pass
            i += 1
            save_pickle(vacansion_hh, path)

    load_pickle(path)
    data_vacansion = load_pickle(path)


    page += 1

    new_url = f'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text={search_name}&from=suggest_post&page={page}'
    driver.get(new_url)
    time.sleep(8)

