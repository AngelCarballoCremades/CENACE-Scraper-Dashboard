"""
There are missing some dates:

dates from 2018-01-04 to 2018-01-08 hour number 24 is missing
"""

import os
import sys
import shutil
import pandas as pd
from functions import get_folder


folder_frame = '..\\files'
energy_flow = 'consumption'
data_type = 'real'
rows_to_skip = 9


def main():

    out_filename = f'{folder_frame}\\{energy_flow}_{data_type}.csv'
    folder,files = get_folder(folder_frame,energy_flow, data_type) # Get folder with files to be joined

    if len(files):

        print(f'{energy_flow}_{data_type}', end='')
        sys.stdout.flush()

        dfs = []

        for i,file in enumerate(files):
            print('.', end='')
            sys.stdout.flush()

            df = pd.read_csv(f'{folder}\\{file}', index_col=False,skiprows=rows_to_skip-1)
            df['Fecha'] = file[36:46]

            dfs.append(df)

        print('Appending...', end='')
        sys.stdout.flush()

        df = pd.concat(dfs)

        print('Ordering...', end='')
        sys.stdout.flush()

        cols = [col.strip(' ').replace(' ','_').lower() for col in df.columns]
        df.columns = cols

        df = df[['sistema','zona_de_carga','fecha','hora','estimacion_de_demanda_por_retiros_(mwh)']]
        df = df.sort_values(by=['sistema','zona_de_carga','fecha','hora'], ascending=True)

        print('Writing File...', end='')
        sys.stdout.flush()


        df.to_csv(out_filename, index=False, float_format='%.3f', header=False)

        print('Done')

        # Showing missing values
        # print(df.hora.value_counts())
        # print(df[df['fecha'] == '2018-01-04'])

    else:
        # If no files where found in folder the system-data is skipped
        print(f'\n{energy_flow}_{data_type} data not found.\n')

    print('----Finished----')


if __name__ == '__main__':
    main()
