import os
import sys
import pdb
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import zipfile

from scraper_prices_month import open_browser, wait_download


years = [1,2,3]

# Download folder, it should have appropiate folder structure
download_folder = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files\\generation\\real'

main_url = r'https://www.cenace.gob.mx/SIM/VISTA/REPORTES/EnergiaGenLiqAgregada.aspx'

# date_textbox_xpath = '/html/body/form/div[4]/div[1]/div[2]/div[3]/div[3]/div[2]/table/tbody/tr/td[1]/div/div[2]/div[{textbox_number}]/div/table/tbody/tr/td[1]'
date_textbox_xpath = r'//*[@id="ctl00_ContentPlaceHolder1_Fecha{Inicial_Final}_dateInput"]'

download_button_xpath = r'//*[@id="DescargaZip"]'


def get_date_string(last_month, last_year):
    month_dict = {
        1:'enero',
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

def date_string_to_numeric(date_string):
    month_dict = {
        1:'enero',
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

    date = date_string.split(' ')

    month = [k for k,v in month_dict.items() if date[0] == v]
    year = date[2]

    return month, year

def check_dates(date_interval, first_date, second_date):

    first_date = date_string_to_numeric(first_date)
    second_date = date_string_to_numeric(second_date)
    first_entered = date_string_to_numeric(date_interval[0])
    second_entered = date_string_to_numeric(date_interval[1])

    if first_date == first_entered and second_date == second_entered:
        return True

    elif first_entered != first_date and first_entered == second_entered:
        return False

    else:
        return True


def main(last_month = 0,last_year = 2018):

    # download = True

    date_interval = get_date_string(last_month, last_year)

    while True:

        if not date_interval:
            print('No information available for dates selected')
            break

        print(date_interval[0], date_interval[1])

        print(f'\nDownloading Energy-type Generation from \n')

        driver = open_browser(download_folder)

        print('Loading page.')
        driver.get(main_url)

        print("Typing date intervals.")

        textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, date_textbox_xpath.format(Inicial_Final='Inicial'))))
        textbox.send_keys(date_interval[0])
        textbox.send_keys(Keys.TAB)
        first_date = textbox.get_attribute("value")


        textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, date_textbox_xpath.format(Inicial_Final = 'Final'))))
        textbox.send_keys(date_interval[1])
        textbox.send_keys(Keys.TAB)
        second_date = textbox.get_attribute("value")


        if not check_dates(date_interval, first_date, second_date):
            print(f'There is no information available for dates selected, information up to {second_date}')
            driver.quit()
            break

        download_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, download_button_xpath)))

        directorio = os.listdir(download_folder)
        download_button.click()
        wait_download(directorio,f'{first_date} to {second_date}', download_folder)

        driver.quit()
        print('Download done.')

        # print('Extracting zip file...')

        # file_name = os.listdir(download_folder)[0]
        # file_path = f'{download_folder}\\{file_name}'
        # # print(directorio)

        # with zipfile.ZipFile(file_path, 'r') as zip_file:
        #     zip_file.extractall(download_folder)

        # print('Removing zip file...')
        # os.remove(file_path)

        # print('Only keeping first-liquidation files...')
        # for file_name in os.listdir(download_folder):
        #     if "Generacion Liquidada_L0" not in file_name:
        #         file_path = f'{download_folder}\\{file_name}'
        #         os.remove(file_path)

        # print('Done')


        break


if __name__ == '__main__':
    main()