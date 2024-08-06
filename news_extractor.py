import re, os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List
from robocorp.tasks import task
from RPA.Excel.Files import Files, Table
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from robocorp import workitems

OUTPUT_DIR = f'{os.getcwd()}/news.xlsx'

def get_items() -> dict:    
  return workitems.inputs.current.payload

def create_table() -> Table:
  table = Table()
  for _ in range(6):
    table.append_column()  
  table.set_row(0,['Title', 'Description', 'Date', 'Picture Filename', '# of query in title/desc', 'Has Money'])
  return table

def count_query(query, title, desc) -> int:
  occurr_title = re.findall(query, title)
  occurr_desc = re.findall(query, desc)
  count = len(occurr_title) + len(occurr_desc)
  return count

def cites_money(text) -> bool:
    pattern = r"""
        (?<!\w)  
        (                 
        \$\d{1,3}(,\d{3})*(\.\d{2})? |  # Matches $11.1 or $111,111.11
        \d+(\.\d{1,2})?\s?(dollars|USD)  # Matches 11 dollars or 11 USD or 11.11 dollars or 11.11 USD
        )                 
        (?!\w)  # Negative lookahead to ensure the match is not followed by a word character
    """
    # Use re.IGNORECASE to make the pattern case-insensitive
    match = re.search(pattern, text, re.VERBOSE | re.IGNORECASE)
    return match is not None


def retrieve_news(params: dict) -> List[List[str]]:  
  ff_options = Options()
  #ff_options.add_argument("--headless")
  driver = webdriver.Firefox(options=ff_options)
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

      news = []

      last_time = datetime.now().timestamp()
      time_limit = (datetime.now() - relativedelta(months=int(params['months']))).timestamp()

      while last_time > time_limit:
        news_tags = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='promo-wrapper']"))
        )

        for news_tag in news_tags:
          last_time = float(news_tag.find_element(By.CLASS_NAME, 'promo-timestamp').get_attribute('data-timestamp'))/1000
          if last_time < time_limit:
            return news
          time = datetime.fromtimestamp(last_time).strftime('%y-%m-%d')
          title = news_tag.find_element(By.CLASS_NAME, 'promo-title').text
          desc = news_tag.find_element(By.CLASS_NAME, 'promo-description').text
          image = news_tag.find_element(By.CLASS_NAME, 'promo-placeholder').get_attribute('href')
          count_q = count_query(params['query'], title, desc)
          has_money = cites_money(f'{title} {desc}')
          news.append([title,desc,time,image,count_q,has_money])

        next_anchor = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='search-results-module-next-page']//a"))
        )
        current_url = driver.current_url
        next_anchor.click()        
        WebDriverWait(driver, 10).until(
            EC.url_changes(current_url)
        )
        
  finally:
      driver.close()

  return news

@task
def extract_news():
  items = get_items()    
  
  table = create_table()
  
  news_list = retrieve_news(items)
    
  print(news_list)
  if len(news_list) == 0:
    return
  for news in news_list:
    table.append_row(news)

  file = Files()
  file.create_workbook(OUTPUT_DIR, sheet_name='News')
  file.append_rows_to_worksheet(table)
  file.save_workbook()