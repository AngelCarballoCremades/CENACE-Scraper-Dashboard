"""
Crea una base de datos desde cero con la información del año actual y el año anterior de todos los sistemas, nodos y mercados.
Debería utilizarse sólo inicialmente.
Modificar folder destino al deseado, debe tener la estructura adecuada.
Se utiliza Firefox
"""

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


# different data to be downloaded
datas = ['PND-MTR','PND-MDA','PML-MTR','PML-MDA']

# 1 = current year, 2 = last year, 3 = lastlast year.... data exists from 2017
years = [1,2,3]

# Download Folder, it should have appropiate folder structure
download_folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files\\{PND_PML}\\{MDA_MTR}'

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

def wait_download(directorio,file_number):
    """Iterates while a file is being downloaded in order to download just one file at a time. To do this a file.part is searched in the download_folder directory, when it disappears, the download has finished. Does not return anything."""
    while directorio == os.listdir(download_folder):
        # Waiting for the download to begin
        pass

    time.sleep(1)
    print(f'File {file_number}.', end = '')

    wait = True
    # Looking for a .part file in download_folder directory
    while wait:
        wait = False
        for file in os.listdir(download_folder):
            if ".part" in file:
                time.sleep(0.5)
                wait = True
                print('.', end = '')
                sys.stdout.flush()
    print('Done')

def get_total_rows(html_code):
    """Takes pages html code, with table loaded, and returns total files available for time selected"""
    soup = BeautifulSoup(html_code, 'lxml')
    table = soup.find('table', {'id':'products', 'class':'products'})
    body = table.find('tbody')
    months = len(body.find_all('tr', {'class':'expanded'}))/3

    # 3 systems and 2 files per system per month
    return int(months*3*2)


# Main code

# This is to measure download times
start_time = time.time()

for data in datas:

    # assigning download folder path for data to be downloaded
    download_folder = download_folder_frame.format(PND_PML = data[:3], MDA_MTR = data[-3:])

    # data page url
    main_url = urls[data]

    # loop to download this years and last's data
    for year_selected in years:

        print(f'\nDOWNLOADING: {data} from {2020 if year_selected == 1 else 2019}\n')

        # setting firefox profile settings
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2) # Do not use default download folder
        profile.set_preference("browser.download.dir", download_folder) # Use selected download folder
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream") # Do not show download popup for selected mime-type files

        print('Opening Browser.')
        driver = webdriver.Firefox(firefox_profile=profile)

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

                directorio = os.listdir(download_folder) # Saves files names in download folder
                xpath_file = xpath_frame.format(t=table, r=row) # Build file's button xpath
                file_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath_file))) #Wait for and get file's button
                file_button.click() # Click file's button
                wait_download(directorio,row) # Wait for download to finish

        print(f'\n{len(os.listdir(download_folder))} FILES DOWNLOADED.\n')

        # Close browser for next year or system to be downloaded
        driver.quit()

        print('YEAR DONE')

    print('............DONE............')

print('.......................................DONE...............................................')
print("--- %s seconds ---" % (time.time() - start_time))