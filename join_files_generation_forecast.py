import os
import sys
import shutil
import pandas as pd
from functions import get_folder


folder_frame = '..\\files'
energy_flow = 'generation'
data_type = 'forecast'
rows_to_skip = 8


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

            df = pd.read_csv(f'{folder}\\{file}', skiprows=rows_to_skip-1, index_col=False)
            df['Fecha'] = file[21:31]
            dfs.append(df)

        print('Appending...', end='')
        sys.stdout.flush()

        df = pd.concat(dfs)

        print('Ordering...', end='')
        sys.stdout.flush()

        df.columns = [column.strip(' ').replace(' ','_').lower() for column in df.columns]
        df = df[['sistema','tipo_de_tecnologia','fecha','hora','pronostico_de_generacion_(mwh)']]
        df = pd.pivot_table(df,
                            values = 'pronostico_de_generacion_(mwh)',
                            index = ['sistema','fecha','hora'],
                            columns = 'tipo_de_tecnologia',
                            fill_value = 0.0)

        df = df.sort_values(by=['sistema','fecha','hora'], ascending=True)

        print('Writing File...', end='')
        sys.stdout.flush()

        df.to_csv(out_filename, float_format='%.3f', header=False)

        print('Done')

    else:
        # If no files where found in folder the system-data is skipped
        print(f'\n{energy_flow}_{data_type} data not found.\n')

    print('----Finished----')


if __name__ == '__main__':
    main()
