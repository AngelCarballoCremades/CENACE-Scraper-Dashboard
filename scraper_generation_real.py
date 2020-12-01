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


def main(last_month = 10,last_year = 2020):

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

        textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, date_textbox_xpath.format(Inicial_Final = 'Inicial'))))
        textbox.send_keys(date_interval[0])
        print(1)

        textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, date_textbox_xpath.format(Inicial_Final = 'Final'))))
        textbox.send_keys(date_interval[1])
        print(2)


        # REVISAR SI EL TEXTO DE LOS CUADROS CAMBIÓ REALMENTE O REGRESÓ AL TEXTO ANTERIOR
        # CONDICIONAL SI TEXTBOX.TEXT == date_interval[0] (ALGO PARECIDO)



        download_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, download_button_xpath)))
        download_button.click()
        print(3)

        directorio = os.listdir(download_folder)
        wait_download(directorio,f'{date_interval[0]} a {date_interval[1]}', download_folder)


        break
#     for month in range(1,len(months)+1):

#         days = len(get_days_of_month(months[month-1]))

#         month_xpath = month_xpath_frame.format(month=month*2-1) # Build info xpath
#         month_info = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, month_xpath))).text # Wait for and get info
#         print(month_info)

#         for day in range(1,days+1):

#             file_date_xpath = file_date_xpath_frame.format(month=month*2, day = day) # File date xpath
#             file_date = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, file_date_xpath))).text # File date

#             download = check_date(date, file_date)

#             if not download:
#                 print(date, file_date)
#                 break

#             file_button_xpath = file_button_xpath_frame.format(month=month*2, day = day)
#             file_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, file_button_xpath))) #Wait for and get file's button

#             directorio = os.listdir(download_folder)
#             file_button.click() # Click file's button
#             wait_download(directorio,file_date, download_folder) # Wait for download to finish

#         if not download:
#             break


#     print(f'\n{len(os.listdir(download_folder))} FILES DOWNLOADED.\n')

#     # Close browser for next year or system to be downloaded
#     driver.quit()

#     print('YEAR DONE')


if __name__ == '__main__':
    main()