import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import zipfile

from functions import *


years = [1,2,3]

# Download folder, it should have appropiate folder structure
download_folder = '..\\files\\generation\\real'

main_url = r'https://www.cenace.gob.mx/SIM/VISTA/REPORTES/EnergiaGenLiqAgregada.aspx'

date_textbox_xpath = r'//*[@id="ctl00_ContentPlaceHolder1_Fecha{Inicial_Final}_dateInput"]'

download_button_xpath = r'//*[@id="DescargaZip"]'


def month_dictionary():

    return {1:'enero',
            2:'febrero',
            3:'marzo',
            4:'abril',
            5:'mayo',
            6:'junio',
            7:'julio',
            8:'agosto',
            9:'septiembre',
            10:'octubre',
            11:'noviembre',
            12:'diciembre'}


def get_date_string(last_month, last_year):

    month_dict = month_dictionary()
    today = datetime.today()
    month = today.month
    year = today.year

    if month > last_month or year > last_year:
        if last_month == 12:
            first_month = 1
            first_year = last_year + 1

        else:
            first_month = last_month + 1
            first_year = last_year

        first_string = f'{month_dict[first_month]} de {first_year}'
        second_string = f'{month_dict[month]} de {year}'

        return [first_string, second_string]


    else:
        return None


def pack_dates(last_month, last_year):

    today = datetime.today()
    month = today.month
    year = today.year

    if year < last_year:
        return None

    if month > last_month or year > last_year:
        dates_packed = []

        while month != last_month or year != last_year:

            if year != last_year:
                dates_packed.append([date_numeric_to_string(last_month + 1, last_year), date_numeric_to_string(12, last_year)])
                last_month = 0
                last_year += 1
            else:
                dates_packed.append(get_date_string(last_month, last_year))
                break

        return dates_packed

    else:
        return None


def date_string_to_numeric(date_string):

    month_dict = month_dictionary()
    date = date_string.split(' ')

    month = [k for k,v in month_dict.items() if date[0] == v]
    year = date[2]

    return [month, year]


def date_numeric_to_string(month, year):

    month_dict = month_dictionary()
    return f'{month_dict[month]} de {year}'


def check_dates(date_interval, first_date, second_date):

    first_date = date_string_to_numeric(first_date)
    second_date = date_string_to_numeric(second_date)
    first_entered = date_string_to_numeric(date_interval[0])
    second_entered = date_string_to_numeric(date_interval[1])

    if first_date == first_entered and second_date == second_entered:
        return True

    if first_entered > first_date:
        return False

    if first_entered == first_date and second_date >= first_date:
        return True

    else:
        return False


def zip_extract_remove(download_folder):

    for file_name in os.listdir(download_folder):
        file_path = f'{download_folder}\\{file_name}'

        with zipfile.ZipFile(file_path, 'r') as zip_file:
            zip_file.extractall(download_folder)

        os.remove(file_path)


def filter_files(download_folder, string_to_keep):

    for file_name in os.listdir(download_folder):
        if string_to_keep not in file_name:
            file_path = f'{download_folder}\\{file_name}'
            os.remove(file_path)


def main(last_month = 0,last_year = 2018):

    print(f'\nDownloading Energy-type Real Generation')
    print(f'Last day on record: {last_month}-{last_year}\n')

    dates_packed = pack_dates(last_month, last_year)

    valid = True
    while True:

        if not dates_packed:
            print('No information available for dates selected')
            break

        driver = open_browser(download_folder)

        print('Loading page.')
        driver.get(main_url)

        for date_interval in dates_packed:

            print("Selecting dates...")

            first_date = textbox_fill(driver = driver,
                                      xpath = date_textbox_xpath.format(Inicial_Final='Inicial'),
                                      date_string = date_interval[0],
                                      attribute = 'value')

            second_date = textbox_fill(driver = driver,
                                       xpath = date_textbox_xpath.format(Inicial_Final='Final'),
                                       date_string = date_interval[1],
                                       attribute = 'value')

            valid = check_dates(date_interval, first_date, second_date)

            if not valid:
                print(f'There is no information available for dates selected, information up to {second_date}')
                driver.quit()
                break

            print('Waiting for download to begin...')

            download_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, download_button_xpath)))
            directorio = os.listdir(download_folder)
            download_button.click()
            wait_download(directorio,f'{first_date} to {second_date}', download_folder)

        if not valid:
            break

        print('Download done.')

        driver.quit()

        print('Extracting zip files...')

        zip_extract_remove(download_folder)
        filter_files(download_folder, string_to_keep="Generacion Liquidada_L0")

        print('------------------------Done------------------------')

        break

    return valid


if __name__ == '__main__':
    main()