"""
Este archivo junta los archivos descargados en *monthly_download.py* y crea archivos *.cvs* por sistema, nodo y sistema.
Debes especificar el folder donde están tus archivos (con la estructura adecuada) en la función get_folder y modificar el folder de destino en el codigo principal.
"""

import pandas as pd
import os
import sys
import shutil

systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']
folder_frame = '..\\files'


def get_folder(system, node_type, market):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""
    folder = f'{folder_frame}\\{node_type}\\{market}'
    files_list = os.listdir(folder)
    files = [file for file in files_list if system in file] # Select files of indicated system by name

    return folder,files


def join_small_csvs(folder, files, system, node_type, market):
    """This functions joins all csv files in 'files' list within 'folder' to the specified file"""

    # values to add to file as columns: system and market
    string_byte = bytes(f'{system},{market},', 'ascii')
    header_byte = bytes(f'Sistema,Mercado,', 'ascii')

    file_number = 1
    complete = False
    i = 0
    files_read = 0

    while not complete:
        out_filename = f'{folder_frame}\\{system}_{node_type}_{market}_{file_number}.csv'

        with open(out_filename, 'wb') as outfile:
            for i, file in enumerate(files[files_read:]):

                print('.', end = '')
                sys.stdout.flush()

                if os.stat(out_filename).st_size/(1024*1024*1024) > 0.95:
                    complete = False
                    break

                files_read += 1

                with open(f'{folder}\\{file}', 'rb') as readfile:
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()
                    readfile.readline()

                    for line in readfile.readlines():
                        outfile.write(string_byte+line)

        if files_read == len(files):
            complete = True
        file_number += 1


def main():
    pass
    for system in systems:
        for node_type in node_types:
            for market in markets:

                folder,files = get_folder(system, node_type, market) # Get folder with files to be joined

                if len(files):

                    print(f'{system}-{node_type}_{market} ', end = '')
                    sys.stdout.flush() # Prints

                    join_small_csvs(folder, files, system, node_type, market)

                    print('Done')

                else:
                    # If no files where found in folder the system-data is skipped
                    print(f'\n{system}_{node_type}_{market} data not found.\n')

    print('----Finished----')


if __name__ == '__main__':
    main()
