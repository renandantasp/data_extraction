import os

ROOT_DIR = os.getcwd()
OUTPUT_DIR = f'{os.getcwd()}/output'
RESULTS_DIR = f'{OUTPUT_DIR}/results'
IMGS_DIR = f'{RESULTS_DIR}/imgs'
EXCEL_PATH = f'{RESULTS_DIR}/news.xlsx'
LOGGING_LEVEL = 'DEBUG' 
LOG_FILE = f'{OUTPUT_DIR}/news_extractor.log'