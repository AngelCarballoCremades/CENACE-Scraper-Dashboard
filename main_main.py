import join_files_prices
import join_files_consumption_forecast
import join_files_consumption_real
import join_files_generation_forecast
import join_files_generation_real
import scraper_generation_real
import scraper_generation_forecast
import scraper_consumption



if __name__ == '__main__':

    # scraper_consumption.main(data_type='forecast')
    # scraper_consumption.main(data_type='real')
    # scraper_generation_forecast.main()
    # scraper_generation_real.main()
    join_files_consumption_forecast.main()
    join_files_consumption_real.main()
    join_files_generation_forecast.main()
    join_files_generation_real.main()
    # join_files_prices.main()
