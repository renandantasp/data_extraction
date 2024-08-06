from typing import List
import os, logging, re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import urllib.request
from utils import count_query, mentions_money
from config import LOG_FILE, IMGS_DIR


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
stream_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def download_image(image_url: str, save_path: str) -> None:
    """Download an image from a URL and save it to a local file."""
    try:
        urllib.request.urlretrieve(image_url, save_path)
        logger.info(f"Image downloaded and saved to {save_path}.")
    except Exception as e:
        logger.error(f"Failed to download image from {image_url}: {e}")

def retrieve_news(params: dict) -> List[List[str]]:  
  ff_options = Options()
  ff_options.add_argument("--headless")
  driver = webdriver.Firefox(options=ff_options)
  driver.get("https://www.latimes.com/")
  
  try:
    logger.info("Starting search for news articles.")

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
        image_url = news_tag.find_element(By.CLASS_NAME, 'image').get_attribute('srcset').split(' ')[0]

        image_filename =  re.sub(r'[^a-zA-Z0-9\s]', '', title) + '.jpg'
        save_path = os.path.join(IMGS_DIR, image_filename)
        download_image(image_url, save_path)

        count_q = count_query(params['query'], title, desc)
        has_money = mentions_money(f'{title} {desc}')
        logger.debug(f"Added news item: {title}")
        
        news.append([title,desc,time,f'{save_path}',count_q,has_money])

      next_anchor = WebDriverWait(driver, 5).until(
          EC.presence_of_element_located((By.XPATH, "//div[@class='search-results-module-next-page']//a"))
      )
      current_url = driver.current_url
      next_anchor.click()        
      WebDriverWait(driver, 10).until(
          EC.url_changes(current_url)
      )        
  except Exception as e:
        logger.error(f"An error occurred: {e}")
  finally:
    driver.close()

  return news
