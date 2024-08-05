from robocorp.tasks import task
from RPA.Excel.Files import Files, Table
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robocorp import workitems
import os

OUTPUT_DIR = f'{os.getcwd()}/news.xlsx'

def get_items() -> dict:    
  return workitems.inputs.current.payload

def create_table() -> Table:
  table = Table()
  for _ in range(6):
    table.append_column()  
  table.set_row(0,['Title', 'Date', 'Description', 'Picture Filename', '# of query in title/desc', 'Has Money'])

def retrieve_news(params: dict) -> dict:  
  driver = webdriver.Firefox()
  driver.get("https://www.latimes.com/")
  try:
      search_button = WebDriverWait(driver, 5).until(
          EC.presence_of_element_located((By.XPATH, "//button[@data-element='search-button']"))
      )
      search_button.click()
      input_form = WebDriverWait(driver, 5).until(
          EC.presence_of_element_located((By.XPATH, "//input[@data-element='search-form-input']"))
      )
      input_form.send_keys(params['query'])
      input_form.send_keys(Keys.ENTER)

      select_sort = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, "//select[@class='select-input']"))
      )
      select = Select(select_sort)
      select.select_by_visible_text('Newest')
      
      filter_xpath = "//label[span[text()='" + params['section'] + "']]//input[@type='checkbox']"
      filter = WebDriverWait(driver, 5).until(
          EC.presence_of_element_located((By.XPATH, filter_xpath))
      )
      if not filter.is_selected():
        filter.click()

      
      
  finally:
      WebDriverWait(driver, 10)

@task
def extract_news():
  items = get_items()    
  table = create_table()
  news = retrieve_news(items)


  file = Files()
  file.create_workbook(OUTPUT_DIR, sheet_name='News')
  file.append_rows_to_worksheet(table)
  file.save_workbook()
  # print(table.data)