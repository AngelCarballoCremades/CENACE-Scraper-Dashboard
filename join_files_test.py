import pandas as pd
import os
import sys
import shutil


folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files'

energy_flows = ['generation','consumption']
data_types = ['real','forecast']

rows_to_skip_dict = {'generation-real':15,
                'generation-forecast':8,
                'consumption-real':[9,16], # Without quotes first, with quotes second
                'consumption-forecast':14}

def get_folder(energy_flow, data_type):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""

    folder = f'{folder_frame}\\{energy_flow}\\{data_type}'
    files = os.listdir(folder)

    return folder,files


def join_csvs(folder, files, energy_flow, data_type):
    """This functions joins all csv files in 'files' list within 'folder' to the specified file"""


    header = 'fecha'
    out_filename = f'{folder_frame}\\{energy_flow}-{data_type}.csv'

    with open(out_filename, 'w') as outfile:
        for i, file in enumerate(files):

            print('.', end = '')
            sys.stdout.flush()

            with open(f'{folder}\\{file}', 'r') as readfile:

                rows_to_skip = check_rows_to_skip(energy_flow, data_type, readfile.readline())

                if i == 0:

                    for j in range(rows_to_skip - 1):
                        readfile.readline()

                    outfile.write(f'{header},{readfile.readline()}')

                else:
                    for j in range(rows_to_skip):
                        readfile.readline()

                for line in readfile.readlines():
                    outfile.write(line)


def check_rows_to_skip(energy_flow, data_type, line):

    rows_to_skip = rows_to_skip_dict[f'{energy_flow}-{data_type}']

    if type(rows_to_skip) == type(0):

        return rows_to_skip - 1

    else:
        if line[0] == '"':
            return rows_to_skip[1] - 1
        else:
            return rows_to_skip[0] - 1


def main():

    for energy_flow in energy_flows:
        for data_type in data_types:

            folder,files = get_folder(energy_flow, data_type) # Get folder with files to be joined

            if len(files):

                print(f'{energy_flow}-{data_type} ', end = '')
                sys.stdout.flush() # Prints

                join_csvs(folder,files,energy_flow, data_type)

                print('Done')

            else:
                # If no files where found in folder the system-data is skipped
                print(f'\n{energy_flow}-{data_type} data not found.\n')

    print('----Finished----')


if __name__ == '__main__':
    main()
