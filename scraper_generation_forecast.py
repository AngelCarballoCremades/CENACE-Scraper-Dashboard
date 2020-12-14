"""
This scraper file downloads data from CENACE web pages.


"""
import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functions import *


# 1 = current year, 2 = last year, 3 = lastlast year.... data exists from 2017
years = [1,2,3]

# Download folder, it should have appropiate folder structure
download_folder = '..\\files\\generation\\forecast'

main_url = r'https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PronosticosGeneracion.aspx?N=245&opc=divCssPronosticosGen&site=Pron%C3%B3sticos%20de%20Generaci%C3%B3n%20Intermitente&tipoArch=C&tipoUni=ALL&tipo=All&nombrenodop='

# xpath frame to select years
xpath_timelapse = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[1]/div/ul/li[{year}]/div/span[3]'

# files button's xpath frame
file_button_xpath_frame = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div[1]/div/table/tbody/tr[{month}]/td[2]/table/tbody/tr[{day}]/td[2]/a[1]/img'

# File date
file_date_xpath_frame = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div[1]/div/table/tbody/tr[{month}]/td[2]/table/tbody/tr[{day}]/td[1]'

# File info xpath frame
month_xpath_frame = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div[1]/div/table/tbody/tr[{month}]/td[2]/span'


def get_months(html_code):
    """Takes pages html code, with table loaded, and returns total files available for time selected"""
    soup = BeautifulSoup(html_code, 'lxml')
    table = soup.find('table', {'id':'products', 'class':'products'})
    body = table.find('tbody')
    months = body.find_all('tr', {'class':'orders'})
    return months


def get_days_of_month(month):

    days = month.find_all('tr')
    return days


def check_date(last_date, file_date):

    year = last_date[:4] == file_date[:4]
    month = last_date[5:7] == file_date[5:7]
    day = last_date[8:] == file_date[8:]

    return not all([year, month, day])


def main(last_date='0000-00-00'):

    download = True

    for year_selected in years:
        print(f'\nDownloading Intermitent Energy Generation Forecast from {2021 - year_selected}')
        print(f'Last day on record: {last_date}\n')

        driver = open_browser(download_folder)

        print('Loading page.')
        driver.get(main_url)

        print('Selecting timelapse')
        driver.find_element_by_xpath(xpath_timelapse.format(year = year_selected)).click()

        print("Waiting for file's table.")
        dummy = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, month_xpath_frame.format(month=1))))

        months = get_months(html_code = driver.page_source)

        for month in range(1,len(months)+1):

            days = len(get_days_of_month(months[month-1]))

            month_xpath = month_xpath_frame.format(month=month*2-1) # Build info xpath
            month_info = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, month_xpath))).text # Wait for and get info
            print(month_info)

            for day in range(1,days+1):

                file_date_xpath = file_date_xpath_frame.format(month=month*2, day = day) # File date xpath
                file_date = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, file_date_xpath))).text # File date

                download = check_date(last_date, file_date)

                if not download:
                    print(last_date, file_date)
                    break

                file_button_xpath = file_button_xpath_frame.format(month=month*2, day = day)
                file_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, file_button_xpath))) #Wait for and get file's button

                directorio = os.listdir(download_folder)
                file_button.click() # Click file's button
                wait_download(directorio,file_date, download_folder) # Wait for download to finish

            if not download:
                break

        print(f'\n{len(os.listdir(download_folder))} FILES DOWNLOADED.\n')

        # Close browser for next year or system to be downloaded
        driver.quit()

        if not download:
            break

        print('YEAR DONE')

    if len(os.listdir(download_folder)) > 0:
        return True

    else:
        return False


if __name__ == '__main__':
    main(last_date = '2020-11-23')