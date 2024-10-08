import os
import os.path
from datetime import datetime
from config import OUTPUT_DIR
from utils import Utils
from RPA.Excel.Files import Files, Table
from news_retriever import NewsRetriever
from base_logger import BaseLogger
from robocorp import workitems

class TaskManager(BaseLogger):
  """
  A class to manage the task of retrieving news articles, processing them, and saving the results to an Excel file.

  The `TaskManager` class inherits from `BaseLogger` to provide logging capabilities. It utilizes the `NewsRetriever` 
  class to fetch news articles from the Los Angeles Times website and processes the retrieved data to save it in an 
  Excel file.
  """
  
  def __init__(self):
    super().__init__(logger_name=__name__)
    self.utils = Utils()
    self.news_retriever = NewsRetriever()

  def get_items(self) -> dict:
    """
      Retrieve input items from workitems.

      This function retrieves the current payload from workitems.inputs and extracts
      the 'query', 'section', and 'months' values. If 'months' is less than or equal to 0,
      it sets 'months' to 1.

      Returns:
      dict: A dictionary containing the 'query', 'section', and 'months' values.
    """
    json = workitems.inputs.current.payload
    payload = dict()
    try:
      payload['query'] = json['query']
    except KeyError as e:
      self.logger.error(f"The 'query' field is missing in the payload, the query will be set to an empty string. {e}")
      payload['query'] = ''

    try:  
      payload['section'] = json['section']
    except KeyError as e:
      self.logger.error(f"The 'section' field is missing in the payload, the section will be set to an empty string. {e}")
      payload['section'] = ''
    
    try:
      payload['months'] = json['months']
    except KeyError as e:
      self.logger.error(f"The 'query' field is missing in the payload, the month will be set to 1. {e}")
      payload['months'] = 1

    if payload['months'] <= 0:
      payload['months'] = 1

    return payload

  def create_table(self) -> Table:
    """
      Create and initialize a table with headers.

      This function creates a new Table instance, appends six columns, and sets the first row
      with specific headers: 'Title', 'Description', 'Date', 'Picture Filename', '# of query in title/desc',
      and 'Has Money'.

      Returns:
      Table: An initialized Table instance with headers set.
    """
    table = Table()
    for _ in range(6):
      table.append_column()  
    table.set_row(0,[
      'Title', 'Description', 'Date', 'Picture Filename', 
      '# of query in title/desc', 'Has Money'
    ])
    return table

  def extract_news(self) -> None:
    """
      Extract news articles and save to an Excel file.

      Returns:
      None  
    """
    items = self.get_items()    
    
    table = self.create_table()
    
    news_list = self.news_retriever.retrieve_news(items)
    self.logger.info(f"Retrieved {len(news_list)} news items.")
      
    if len(news_list) == 0:
      return
    for news in news_list:
      table.append_row(news)

    file = Files()
    now = datetime.now()
    now = now.strftime('%y-%m-%d')
    query = self.utils.normalize_str(items['query'])
    section = self.utils.normalize_str(items['section'])
    filepath = f'{OUTPUT_DIR}/latimes_{now}_{query}_{section}.xlsx'
    file.create_workbook(filepath, sheet_name='News')
    file.append_rows_to_worksheet(table)
    file.save_workbook()
    if os.path.isfile(filepath):    
      self.logger.info(f"News articles saved to {filepath}.")
    else:
      self.logger.error(f"Error to save {filepath}.")