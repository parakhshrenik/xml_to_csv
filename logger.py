import logging
import os


def _check_output_dir_exists():
    if not os.path.exists('Logs'):
        os.makedirs('Logs')

def get_logger():
    _check_output_dir_exists()
    logging.basicConfig(level=logging.INFO, filename='Logs/xml_to_csv.log', filemode='a', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('xml_to_csv')
    return logger
