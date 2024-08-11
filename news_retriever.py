from typing import List
import os
import logging
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
from selenium.webdriver.remote.webdriver import WebDriver
import urllib.request
from utils import Utils
from config import LOG_FILE, OUTPUT_DIR

class NewsRetriever:
  
    def __init__(self):
        self.utils = Utils()
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(LOG_FILE)
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger

    def download_image(self, image_url: str, save_path: str) -> None:
        try:
            urllib.request.urlretrieve(image_url, save_path)
            self.logger.info(f"Image downloaded and saved to {save_path}.")
        except Exception as e:
            self.logger.error(f"Failed to download image from {image_url}: {e}")

    def retrieve_image(self, news_tag: WebElement, title: str) -> str:
        save_path = 'image not found'
        try:
            image_url = news_tag.find_element(By.CLASS_NAME, 'image').get_attribute('srcset').split(' ')[0]
            image_filename = self.utils.normalize_str(title) + '.jpg'
            save_path = os.path.join(OUTPUT_DIR, image_filename)
            self.download_image(image_url, save_path)
        except Exception as e:
            self.logger.error(f'Error saving image: {e}')
        return save_path

    def apply_filter(self, driver: WebDriver, filter_text: str) -> None:
        filter_xpath = f"//label[span[text()='{filter_text}']]//input[@type='checkbox']"
        try:
            filter = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, filter_xpath))
            )
            if not filter.is_selected():
                filter.click()
        except TimeoutException:
            self.logger.error('Filter does not exist. Continuing without applying any filter')

    def init_webdriver(self) -> WebDriver:
        ff_options = Options()
        #ff_options.add_argument("--headless")
        driver = webdriver.Firefox(options=ff_options)
        driver.get("https://www.latimes.com/")
        return driver

    def search_news(self, driver: WebDriver, query: str) -> None:
        search_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-element='search-button']"))
        )
        search_button.click()
        input_form = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-element='search-form-input']"))
        )
        input_form.send_keys(query)
        input_form.send_keys(Keys.ENTER)

    def sort_news_by_newest(self, driver: WebDriver) -> None:
        select_sort = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@class='select-input']"))
        )
        select = Select(select_sort)
        select.select_by_visible_text('Newest')

    def get_news_elements(self, driver: WebDriver) -> List[WebElement]:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='promo-wrapper']"))
        )

    def get_news_data(self, news_tag: WebElement, params: dict) -> List[str]:
        last_time = float(news_tag.find_element(By.CLASS_NAME, 'promo-timestamp').get_attribute('data-timestamp')) / 1000
        time = datetime.fromtimestamp(last_time).strftime('%y-%m-%d')
        title = news_tag.find_element(By.CLASS_NAME, 'promo-title').text
        desc = news_tag.find_element(By.CLASS_NAME, 'promo-description').text
        save_path = self.retrieve_image(news_tag, title)
        count_q = self.utils.count_query(params['query'], title, desc)
        has_money = self.utils.mentions_money(f'{title} {desc}')
        self.logger.debug(f"Added news item: {title}")
        return [title, desc, time, save_path, count_q, has_money]

    def click_next_page(self, driver: WebDriver) -> None:
        next_anchor = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='search-results-module-next-page']//a"))
        )
        current_url = driver.current_url
        next_anchor.click()
        WebDriverWait(driver, 10).until(EC.url_changes(current_url))

    def retrieve_news(self, params: dict) -> List[List[str]]:
        driver = self.init_webdriver()
        news = []
        try:
            self.logger.info("Starting search for news articles.")
            self.search_news(driver, params['query'])
            self.sort_news_by_newest(driver)
            self.apply_filter(driver, params['section'])

            last_time = datetime.now().timestamp()
            time_limit = (datetime.now() - relativedelta(months=int(params['months']))).timestamp()

            while last_time > time_limit:
                news_tags = self.get_news_elements(driver)
                for news_tag in news_tags:
                    last_time = float(news_tag.find_element(By.CLASS_NAME, 'promo-timestamp').get_attribute('data-timestamp')) / 1000
                    if last_time < time_limit:
                        return news
                    news.append(self.get_news_data(news_tag, params))
                self.click_next_page(driver)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            driver.close()
        return news
