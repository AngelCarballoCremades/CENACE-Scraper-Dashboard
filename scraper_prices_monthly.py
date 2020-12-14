"""
Crea una base de datos desde cero con la información del año actual y el año anterior de todos los sistemas, nodos y mercados.
Debería utilizarse sólo inicialmente.
Modificar folder destino al deseado, debe tener la estructura adecuada.
Se utiliza Firefox
"""

import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions import *

# different data to be downloaded
node_types = ['PND','PML']
markets = ['MDA','MTR']

# 1 = current year, 2 = last year, 3 = lastlast year.... data exists from 2017
years = [1,2,3]

# Download Folder, it should have appropiate folder structure
download_folder_frame = '..\\files\\{node_type}\\{market}'

# urls to all data
urls = {'PML-MDA':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PreciosEnergiaSisMEM.aspx?N=6&opc=divCssPreEnergia&site=Precios%20de%20la%20energ%C3%ADa/Precios%20Marginales%20Locales/MDA/Mensuales&tipoArch=C&tipoUni=SIN&tipo=Mensuales&nombrenodop=Precios%20Marginales%20Locales',
'PML-MTR':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PreciosEnergiaSisMEM.aspx?N=9&opc=divCssPreEnergia&site=Precios%20de%20la%20energ%C3%ADa/Precios%20Marginales%20Locales/MTR/Mensuales&tipoArch=C&tipoUni=SIN&tipo=Mensuales&nombrenodop=Precios%20Marginales%20Locales',
'PND-MDA':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PreciosEnergiaSisMEM.aspx?N=27&opc=divCssPreEnergia&site=Precios%20de%20la%20energ%C3%ADa/Precios%20de%20Nodos%20Distribuidos/MDA/Mensuales&tipoArch=C&tipoUni=SIN&tipo=Mensuales&nombrenodop=Precios%20de%20Nodos%20Distribuidos',
'PND-MTR':'https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PreciosEnergiaSisMEM.aspx?N=30&opc=divCssPreEnergia&site=Precios%20de%20la%20energ%C3%ADa/Precios%20de%20Nodos%20Distribuidos/MTR/Mensuales&tipoArch=C&tipoUni=SIN&tipo=Mensuales&nombrenodop=Precios%20de%20Nodos%20Distribuidos'}

# xpath frame to select years
xpath_timelapse = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[1]/div/ul/li[{year}]/div/span[3]'

# files button's xpath frame
xpath_frame = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div[1]/div/table/tbody/tr[{t}]/td[2]/table/tbody/tr[{r}]/td[2]/a[1]/img'

# File info xpath frame
xpath_frame_info = '/html/body/form/div[4]/div[1]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div[1]/div/table/tbody/tr[{t}]/td[2]/span'


def get_total_rows(html_code):
    """Takes pages html code, with table loaded, and returns total files available for time selected"""

    soup = BeautifulSoup(html_code, 'lxml')
    table = soup.find('table', {'id':'products', 'class':'products'})
    body = table.find('tbody')
    months = len(body.find_all('tr', {'class':'expanded'}))/3

    # 3 systems and 2 files per system per month
    return int(months*3*2)


def main():

    # Measure download time
    start_time = time.time()

    for node_type in node_types:

        for market in markets:

            # assigning download folder path for data to be downloaded
            download_folder = download_folder_frame.format(node_type = node_type, market = market)

            # data page url
            main_url = urls[f'{node_type}-{market}']

            # loop to download this years and last's data
            for year_selected in years:

                print(f'\nDOWNLOADING: {node_type}-{market} from {2021 - year_selected}\n')

                driver = open_browser(download_folder)

                print('Loading page.')
                driver.get(main_url)

                print('Selecting timelapse')
                driver.find_element_by_xpath(xpath_timelapse.format(year = year_selected)).click()

                print("Waiting for file's table.")
                dummy = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath_frame_info.format(t=1))))

                files_available = get_total_rows(driver.page_source)
                print(f'\n{files_available} files available\n')

                for table in range(2,files_available+1,2):

                    xpath_info = xpath_frame_info.format(t=table-1) # Build info xpath
                    file_info = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath_info))).text # Wait for and get info
                    print(file_info)

                    for row in range(1,3):

                        xpath_file = xpath_frame.format(t=table, r=row) # Build file's button xpath
                        # directorio = os.listdir(download_folder) # Saves files names in download folder

                        # file_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath_file))) #Wait for and get file's button
                        # file_button.click() # Click file's button

                        directorio = download_by_xpath(driver, download_folder, xpath_file)
                        wait_download(directorio,row, download_folder) # Wait for download to finish

                print(f'\n{len(os.listdir(download_folder))} FILES DOWNLOADED.\n')

                # Close browser for next year or system to be downloaded
                driver.quit()

                print('YEAR DONE')

            print(f'............{node_type}-{market} DONE............')

    print('.......................................DONE...............................................')
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    main()