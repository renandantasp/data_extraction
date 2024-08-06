import os
from config import ROOT_DIR, OUTPUT_DIR, IMGS_DIR, EXCEL_PATH, RESULTS_DIR
from robocorp.tasks import task
from RPA.Excel.Files import Files, Table
from news_retriever import retrieve_news

from robocorp import workitems

def get_items() -> dict:
  """Retrieve input items from workitems."""

  return workitems.inputs.current.payload

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
  if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
  if not os.path.exists(IMGS_DIR):
    os.makedirs(IMGS_DIR)
    
  if len(news_list) == 0:
    return
  for news in news_list:
    table.append_row(news)

  file = Files()
  
  file.create_workbook(EXCEL_PATH, sheet_name='News')
  file.append_rows_to_worksheet(table)
  file.save_workbook()