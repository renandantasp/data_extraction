from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files, Table
from robocorp import workitems
import os


OUTPUT_DIR = f'{os.getcwd()}/news.xlsx'

def get_items():    
  return workitems.inputs.current.payload

def create_header(table: Table):  
  header_row = ['Title', 'Date', 'Description', 'Picture Filename', '# of query in title/desc', 'Has Money']
  table.append_row(header_row)

  
@task
def extract_news():
  get_items()  
  
  table = Table()
  create_header(table)

  ## do the news thing
  news = 10
  test = ['test','test','test','test','test','test']
  for _ in range(news):
    table.append_row(test)  

  file = Files()
  file.create_workbook(OUTPUT_DIR, sheet_name='News')
  file.set_cell_values("A1", table)
  file.save_workbook()