import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_path(main_folder = 'files', a = '', b = ''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', main_folder, a, b))


def make_directory(main_folder = 'files'):
    """Modificar descargas con path completo"""

    os.makedirs(get_path(main_folder = main_folder, a = 'PML', b='MDA'))
    os.makedirs(get_path(main_folder = main_folder, a = 'PML', b = 'MTR'))
    os.makedirs(get_path(main_folder = main_folder, a = 'PND', b = 'MDA'))
    os.makedirs(get_path(main_folder = main_folder, a = 'PND', b = 'MTR'))
    os.makedirs(get_path(main_folder = main_folder, a = 'generation', b = 'real'))
    os.makedirs(get_path(main_folder = main_folder, a = 'generation', b = 'forecast'))
    os.makedirs(get_path(main_folder = main_folder, a = 'consumption', b = 'real'))
    os.makedirs(get_path(main_folder = main_folder, a = 'consumption', b = 'forecast'))
    os.makedirs(get_path(main_folder = main_folder, a = 'descargas'))


def wait_download(directorio,file_number, download_folder):
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


def open_browser(download_folder):
    """Function description..."""

    profile = webdriver.FirefoxProfile()

    # Do not use default download folder
    profile.set_preference("browser.download.folderList", 2)

    # Use selected download folder
    profile.set_preference("browser.download.dir", download_folder)

    # Do not show download popup for selected mime-type files
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream, application/zip")

    print('Opening Browser.')
    driver = webdriver.Firefox(firefox_profile=profile)

    return driver

def download_by_xpath(driver, folder_path, xpath):
    """"""
    # Find element
    download_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))

    # Get before-download directory content
    directory = os.listdir(folder_path)

    # Click button and begin download
    download_button.click()

    return directory

def postgres_password(file_path = 'psql_password.txt'):

    with open(file_path, 'r') as file:
        params = {
        'host':file.readline()[:-1],
        'user':file.readline()[:-1],
        'password':file.readline()[:-1]
        }

    return params


def textbox_fill(driver, xpath, date_string, attribute):

    textbox = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
    textbox.send_keys(date_string)
    textbox.send_keys(Keys.TAB)
    time.sleep(0.1)

    return textbox.get_attribute(attribute)


def get_folder(subfolder_1 = '', subfolder_2 = ''):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""

    folder = get_path(a = subfolder_1, b = subfolder_2)
    # folder = f'{folder_frame}\\{subfolder_1}'

    # if subfolder_2:
    #     folder = f'{folder_frame}\\{subfolder_1}\\{subfolder_2}'

    files = os.listdir(folder)

    return folder,files


def upload_file_to_database(folder, cursor, table_name, sep = ','):

    files = get_files_names(folder, table_name)
    table = table_name

    for file in files:
        print(f"Uploading {file} to table {table}...", end='')
        sys.stdout.flush()

        file_path = f"{folder}\\{file}"
        # print(file_path)
        with open(file_path, 'rb') as f:
            cursor.copy_from(f, table.lower(), sep=sep)
            print('Done')


def get_files_names(folder, string):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""
    files_list = os.listdir(folder)
    files = [file for file in files_list if string in file]
    return files


def delete_files(folder, subfolder=''):

    # folder = f'{folder}\\{subfolder}'
    print(f'Deleting {folder}')
    files = files_list = os.listdir(folder)
    for file in files:
        os.remove(f'{folder}\\{file}')

def get_download_file_name(file_name = 'dashboard_energia_mexico_datos'):

    folder = get_path(a = 'descargas')
    files = os.listdir(folder)
    i = 1
    keep = True

    while keep:
        keep = False
        for file in files:
            if file_name in file:
                if f'({i-1})' in file_name:
                    file_name = file_name.replace(f"({i-1})", '')
                file_name += f'({i})'
                i += 1
                keep = True
                break

    return file_name + '.csv'

if __name__ == '__main__':
    pass