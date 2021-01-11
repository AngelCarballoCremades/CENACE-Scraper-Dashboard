import time
from functions import *

import join_files_prices
import join_files_consumption_forecast
import join_files_consumption_real
import join_files_generation_forecast
import join_files_generation_real

import scraper_prices_monthly
import scraper_prices_daily
import scraper_generation_real
import scraper_generation_forecast
import scraper_consumption

import SQL_make_database
import update_database


if __name__ == '__main__':

    start = time.time()

    make_directory()

    scraper_prices_monthly.main()
    join_files_prices.main()

    scraper_consumption.main(data_type='forecast')
    join_files_consumption_forecast.main()

    scraper_consumption.main(data_type='real')
    join_files_consumption_real.main()

    scraper_generation_forecast.main()
    join_files_generation_forecast.main()

    scraper_generation_real.main()
    join_files_generation_real.main()

    SQL_make_database.main()
    update_database.main()

    end = time.time()

    print(f'--------------------------Total time: {end-start}--------------------------------')

