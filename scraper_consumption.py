

import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta, datetime
import zipfile

from functions import *


# Download folder, it should have appropiate folder structure
download_folder_frame = '..\\files\\consumption'

urls = {'forecast':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/PronosticosDemanda.aspx',
        'real':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx'}

date_textbox_xpath = {'forecast':'//*[@id="ctl00_ContentPlaceHolder1_RadDatePickerF{I_F}Retiro_dateInput"]',
                      'real':'//*[@id="ctl00_ContentPlaceHolder1_RadDatePickerF{I_F}VisualizarPorRetiros_dateInput"]'}

download_button_xpath = {'forecast':'//*[@id="ctl00_ContentPlaceHolder1_DescargaArchivosRetiro"]',
                         'real':'//*[@id="ctl00_ContentPlaceHolder1_DescargarArchivosCsv_PorRetiros"]'}

def check_textbox_class(textbox_class):

    return not textbox_class == 'riTextBox riError'


def get_date_interval(last_date):

    today = date.today()

    last_date = datetime.strptime(last_date, '%Y-%m-%d').date()
    first_date = last_date + timedelta(days = 1) # Date to start asking for (last_date plus 1 day)
    second_date = today + timedelta(days = 1)

    if first_date > second_date:
        return None

    return [first_date, second_date]


def textbox_fill(driver, xpath, date, attribute):

    textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
    textbox.send_keys(date)
    textbox.send_keys(Keys.TAB)
    time.sleep(0.1)

    return textbox.get_attribute(attribute)


def zip_extract_remove(download_folder):

    file_name = os.listdir(download_folder)[0]
    file_path = f'{download_folder}\\{file_name}'

    with zipfile.ZipFile(file_path, 'r') as zip_file:
        zip_file.extractall(download_folder)

    os.remove(file_path)


def filter_files(download_folder, string_to_keep):

    for file_name in os.listdir(download_folder):
        if string_to_keep not in file_name:
            file_path = f'{download_folder}\\{file_name}'
            os.remove(file_path)


def main(last_date = None, data_type = None):


    if data_type not in ['forecast','real']:
        raise

    if not last_date:

        if data_type == 'forecast':
            last_date = '2019-01-09'

        elif data_type == 'real':
            last_date = '2017-12-31'

        else:
            raise

    download_folder = f'{download_folder_frame}\\{data_type}'

    print(f'\nDownloading Energy Consumption {data_type.upper()}')
    print(f'Last date on database: {last_date}\n')

    date_interval = get_date_interval(last_date)

    while True:

        if not date_interval:
            print('No information available for dates selected')
            break

        driver = open_browser(download_folder)

        print('Loading page.')
        driver.get(urls[data_type])

        print("Selecting dates...")
        download = True

        while True:

            first_date_class = textbox_fill(driver = driver,
                                            xpath = date_textbox_xpath[data_type].format(I_F='I'),
                                            date = date_interval[0].strftime('%d/%m/%Y'),
                                            attribute = 'class')

            second_date_class = textbox_fill(driver = driver,
                                             xpath=date_textbox_xpath[data_type].format(I_F='F'),
                                             date=date_interval[1].strftime('%d/%m/%Y'),
                                             attribute = 'class')

            if not check_textbox_class(second_date_class):

                date_interval[1] -= timedelta(days = 1)
                print('.', end='')
                sys.stdout.flush()
                continue

            print(f'Information available up to {date_interval[1]}')

            if not check_textbox_class(first_date_class):
                print('There is not information available yet.')
                download = False

            break

        if not download:
            driver.quit()
            break

        print('Waiting for download to begin...')

        download_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, download_button_xpath[data_type])))
        directorio = os.listdir(download_folder)
        download_button.click()
        wait_download(directorio,'', download_folder)

        driver.quit()
        print('Download done.')

        print('Extracting zip files...')

        zip_extract_remove(download_folder)

        if data_type == 'real':
            filter_files(download_folder, 'Retiro_0')

        print('------------------------Done------------------------')

        break

    return download


if __name__ == '__main__':
    for data_type in ['forecast', 'real']:
        main(data_type = data_type)