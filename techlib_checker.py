import os
import atexit
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
import logging
import configparser

cfg = configparser.ConfigParser()


def handle_config():
    if not os.path.exists('config.ini'):
        cfg['Main'] = {
            'url': 'https://www.techlib.cz/',
            'csv_path': 'data/',
            'data_save_interval': 300000,
        }

        cfg['Logging'] = {
            'path': "data/log/",
            'report_interval': 3600000,
        }
        cfg.write(open('config.ini', 'w'))
        print('config.ini file created! Exiting application...')
        exit()
    else:
        # Read File
        cfg.read('config.ini')


if __name__ == '__main__':
    def exit_handler():
        logging.info("Application is exiting...")
        logging.info("-------------------------")
    atexit.register(exit_handler)

    # config
    handle_config()
    url = cfg['Main']['url']
    csv_path = cfg['Main']['csv_path']
    data_save_interval = int(cfg['Main']['data_save_interval'])
    report_interval = int(cfg['Logging']['report_interval'])
    logging_path = cfg['Logging']['path']

    # vars
    report_elapsed = 0
    report_successful_count = 0

    # logging
    file_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(logging_path):
        os.makedirs(logging_path)
    logging.basicConfig(filename=f"{logging_path}techlib_checker_{file_date}.log",
                        filemode='a',
                        format='%(asctime)s.%(msecs)03d (%(name)s) [%(levelname)s] - %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)



    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element containing the number of persons in the library
        population = int(soup.select('.text-center span')[0].text)

        # Write the number of persons to a CSV file
        with open(f"{csv_path}techlib_data_{file_date}.csv", 'a', newline='') as csvfile:
            fieldnames = ['date', 'persons']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writerow({'date': datetime.datetime.now().isoformat(), 'persons': population})
        report_successful_count += 1 # if successful add it to the counter
    except Exception as e:
        logging.error(f"Check failed! ({str(e)})")
    finally:
        report_elapsed += data_save_interval

        # report
        if report_elapsed >= report_interval:
            logging.info(f"{report_successful_count} out of {int(report_interval/data_save_interval)} checks have been successfull!")
            report_elapsed = 0
            report_successful_count = 0

        # sleep
        logging.debug(f"Sleeping for {data_save_interval/1000}s")
        time.sleep(data_save_interval)
