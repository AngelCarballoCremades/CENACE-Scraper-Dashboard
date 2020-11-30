"""
Este archivo junta los archivos descargados en *monthly_download.py* y crea archivos *.cvs* por sistema, nodo y sistema.
Debes especificar el folder donde están tus archivos (con la estructura adecuada) en la función get_folder y modificar el folder de destino en el codigo principal.
"""

import pandas as pd
import os
import sys
import shutil

# Data and systems to join
datas = ['PND-MTR','PND-MDA','PML-MTR','PML-MDA']
systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']

folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files'
def get_folder(data,system):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""
    folder = f'{folder_frame}\\{data[:3]}\\{data[-3:]}'
    files_list = os.listdir(folder)
    files = [file for file in files_list if system in file] # Select files of indicated system by name

    # Make smaller files
    # if system == 'SIN' and data == 'PML':
    #     big_files =
    #     while True:



    return folder,files

def get_file_path(node_type, system, data):
    return f'{folder_frame}\\{system}-{node_type}-{data}.csv'

def join_small_csvs(folder, files, system, data):
    """This functions joins all csv files in 'files' list within 'folder' to the specified file"""

    # values to add to file as columns: system and market
    market = data[-3:]
    string_byte = bytes(f'{system},{market},', 'ascii')
    header_byte = bytes(f'Sistema,Mercado,', 'ascii')

    file_number = 1
    complete = False
    i = 0
    files_read = 0

    while not complete:
        out_filename = f'{folder_frame}\\{system}-{data}-{file_number}.csv'

        with open(out_filename, 'wb') as outfile:
            for i, file in enumerate(files[files_read:]):

                print('.', end = '')
                sys.stdout.flush()

                if os.stat(out_filename).st_size/(1024*1024*1024) > 0.95:
                    complete = False
                    break

                files_read += 1

                with open(f'{folder}\\{file}', 'rb') as readfile:
                    # if i == 0:
                    #     for j in range(7):
                    #         readfile.readline()
                    #     line = readfile.readline()
                    #     outfile.write(header_byte+line)
                    # else:
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




def join_big_csvs(node_types, systems, markets):
    """This functions joins all csv files created in join_small_csvs depending on node type (PND or PML)"""
    for node in node_types:

        print(node)
        out_filename = f'{folder_frame}\\{node}.csv'

        with open(out_filename, 'wb') as outfile:

            for i,system in enumerate(systems):
                for j,market in enumerate(markets):

                    file = f'{system}-{node}-{market}.csv'
                    print(f'Joining {file}')

                    with open(f'{folder_frame}\\{file}', 'rb') as readfile:

                        if i != 0 or j != 0:
                            readfile.readline()

                        shutil.copyfileobj(readfile, outfile, length=16*1024*1024)

                    os.remove(f'{folder_frame}\\{file}')

        print(f'{node} Done.')


# Main code
for system in systems:

    for data in datas:

        folder,files = get_folder(data, system) # Get folder with files to be joined

        if len(files):

            print(f'{system}-{data} ', end = '')
            sys.stdout.flush() # Prints

            join_small_csvs(folder,files,system,data)

            print('Done')

        else:
            # If no files where found in folder the system-data is skipped
            print(f'\n{system}-{data} data not found.\n')

print('Finished joining files.')
# print('Merging by node type.')

# join_big_csvs(node_types, systems, markets)

print('----Finished----')



