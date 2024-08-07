import os, os.path, logging
from datetime import datetime
from config import OUTPUT_DIR, LOGGING_LEVEL, LOG_FILE
from utils import normalize_str
from robocorp.tasks import task
from RPA.Excel.Files import Files, Table
from news_retriever import retrieve_news
from robocorp import workitems

logging.basicConfig(level=LOGGING_LEVEL, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def get_items() -> dict:
  """Retrieve input items from workitems."""
  json = workitems.inputs.current.payload
  payload = dict()
  payload['query'] = json['query']
  payload['section'] = json['section']
  payload['months'] = json['months']
  if payload['months'] <= 0:
    payload['months'] = 1

  return payload

def create_table() -> Table:
  """Create and initialize a table with headers."""
  table = Table()
  for _ in range(6):
    table.append_column()  
  table.set_row(0,[
    'Title', 'Description', 'Date', 'Picture Filename', 
    '# of query in title/desc', 'Has Money'
  ])
  return table

@task
def extract_news() -> None:
  """Extract news articles and save to an Excel file."""
  items = get_items()    
  
  table = create_table()
  
  news_list = retrieve_news(items)
  logger.info(f"Retrieved {len(news_list)} news items.")
    
  if len(news_list) == 0:
    return
  for news in news_list:
    table.append_row(news)

  file = Files()
  now = datetime.now()
  now = now.strftime('%y-%m-%d')
  query = normalize_str(items['query'])
  section = normalize_str(items['section'])
  filepath = f'{OUTPUT_DIR}/latimes_{now}_{query}_{section}.xlsx'
  file.create_workbook(filepath, sheet_name='News')
  file.append_rows_to_worksheet(table)
  file.save_workbook()
  if os.path.isfile(filepath):    
    logger.info(f"News articles saved to {filepath}.")
  else:
    logger.error(f"Error to save {filepath}.")