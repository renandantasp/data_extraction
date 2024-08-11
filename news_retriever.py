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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import urllib.request
from utils import Utils
from config import LOG_FILE, OUTPUT_DIR

class NewsRetriever:
  
  def __init__(self):
    self.utils = Utils()
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(LOG_FILE)
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    self.logger.addHandler(file_handler)
    self.logger.addHandler(stream_handler)

  def download_image(self, image_url: str, save_path: str) -> None:
    """
      Download an image from a URL and save it to a local file.

      Parameters:
      image_url (str): The URL of the image to download.
      save_path (str): The local file path where the image will be saved.

      Returns:
      None
    """
    try:
        urllib.request.urlretrieve(image_url, save_path)
        self.logger.info(f"Image downloaded and saved to {save_path}.")
    except Exception as e:
        self.logger.error(f"Failed to download image from {image_url}: {e}")

  def retrieve_image(self, news_tag: WebElement, title: str) -> None:
    save_path = 'image not found'
    try:
      image_url = news_tag.find_element(By.CLASS_NAME, 'image').get_attribute('srcset').split(' ')[0]

      image_filename =  self.utils.normalize_str(title) + '.jpg'
      save_path = os.path.join(OUTPUT_DIR, image_filename)
      self.download_image(image_url, save_path)
    except Exception as e:
      self.logger.error(f'Erro saving image. {e}')
    
  def retrieve_news(self, params: dict) -> List[List[str]]:  
    """
      Retrieve news articles from the Los Angeles Times website based on specified parameters.

      Parameters:
      params (dict): A dictionary containing the query, section and months parameters for filtering the news articles.

      Returns:
      List[List[str]]: A list of news articles, where each article is represented as a list containing the title, description, date, image path, query count, and money mention status.
    """
    ff_options = Options()
    #ff_options.add_argument("--headless")
    driver = webdriver.Firefox(options=ff_options)
    driver.get("https://www.latimes.com/")
    
    news = []
    
    try:
      self.logger.info("Starting search for news articles.")

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
      
      try:
        filter = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, filter_xpath))
        )
        if not filter.is_selected():
          filter.click()    
      except TimeoutException:
        self.logger.error('Filter does not exist. Continuing without applying any filter')

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
          save_path = 'image not found'
          
          self.retrieve_image(news_tag, title)

          count_q = self.utils.count_query(params['query'], title, desc)
          has_money = self.utils.mentions_money(f'{title} {desc}')
          self.logger.debug(f"Added news item: {title}")
          
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
          self.logger.error(f"An error occurred: {e}")
    finally:
      driver.close()

    return news
