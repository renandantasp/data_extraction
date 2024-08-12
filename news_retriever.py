from typing import List
import os
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
from base_logger import BaseLogger
from utils import Utils
from config import OUTPUT_DIR

class NewsRetriever(BaseLogger):
  
    def __init__(self):
        super().__init__(logger_name=__name__)
        self.utils = Utils()

    def download_image(self, image_url: str, save_path: str) -> None:
        """
        Downloads an image from a URL and saves it to a local file.

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

    def retrieve_image(self, news_tag: WebElement, title: str) -> str:
        """
        Retrieves the image URL from a news tag, downloads it, and returns the local save path.

        Parameters:
        news_tag (WebElement): The web element containing the news article.
        title (str): The title of the news article.

        Returns:
        str: The local file path where the image is saved.
        """
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
        """
        Applies a filter on the news search results.

        Parameters:
        driver (WebDriver): The web driver instance.
        filter_text (str): The text of the filter to apply.

        Returns:
        None
        """
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
        """
        Initializes the web driver for browsing.

        Returns:
        WebDriver: Initialized web driver instance.
        """
        ff_options = Options()
        ff_options.add_argument("--headless")
        driver = webdriver.Firefox(options=ff_options)
        driver.get("https://www.latimes.com/")
        return driver

    def search_news(self, driver: WebDriver, query: str) -> None:
        """
        Searches for news articles based on the query.

        Parameters:
        driver (WebDriver): The web driver instance.
        query (str): The search query.

        Returns:
        None
        """
        try: 
          search_button = WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.XPATH, "//button[@data-element='search-button']"))
          )
          search_button.click()
          input_form = WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.XPATH, "//input[@data-element='search-form-input']"))
          )
          input_form.send_keys(query)
          input_form.send_keys(Keys.ENTER)
        except TimeoutException as e:
          self.logger.error(f'Error trying to search for the query. {e}')

    def sort_news_by_newest(self, driver: WebDriver) -> None:
        """
        Sorts the news articles by newest first.

        Parameters:
        driver (WebDriver): The web driver instance.

        Returns:
        None
        """
        try:
          select_sort = WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.XPATH, "//select[@class='select-input']"))
          )
          select = Select(select_sort)
          select.select_by_visible_text('Newest')
        except TimeoutException as e:
          self.logger.error(f"Error trying to sort by newest. {e}")

    def get_news_elements(self, driver: WebDriver) -> List[WebElement]:
        """
        Retrieves the news elements from the search results.

        Parameters:
        driver (WebDriver): The web driver instance.

        Returns:
        List[WebElement]: List of web elements containing news articles.
        """
        try:
          return WebDriverWait(driver, 5).until(
              EC.presence_of_all_elements_located((By.XPATH, "//div[@class='promo-wrapper']"))
          )
        except TimeoutException as e:
          self.logger.error(f"Error trying to get news elements. {e}")

    def get_news_data(self, news_tag: WebElement, params: dict) -> List[str]:
        """
        Extracts news data from a web element.

        Parameters:
        news_tag (WebElement): The web element containing the news article.
        params (dict): Dictionary of search parameters.

        Returns:
        List[str]: A list containing the news title, description, date, image path, query count, and money mention status.
        """
        try:
          last_time = float(news_tag.find_element(By.CLASS_NAME, 'promo-timestamp').get_attribute('data-timestamp')) / 1000
          time = datetime.fromtimestamp(last_time).strftime('%y-%m-%d')
          title = news_tag.find_element(By.CLASS_NAME, 'promo-title').text
          desc = news_tag.find_element(By.CLASS_NAME, 'promo-description').text
          save_path = self.retrieve_image(news_tag, title)
          count_q = self.utils.count_query(params['query'], title, desc)
          has_money = self.utils.mentions_money(f'{title} {desc}')
          self.logger.debug(f"Added news item: {title}")
          return [title, desc, time, save_path, count_q, has_money]
        except Exception as e:
          self.logger(f"Error trying to retrieve info from news' elements. {e}")

    def click_next_page(self, driver: WebDriver) -> None:
        """
        Navigates to the next page of the search results.

        Parameters:
        driver (WebDriver): The web driver instance.

        Returns:
        None
        """
        try:
          next_anchor = WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.XPATH, "//div[@class='search-results-module-next-page']//a"))
          )
          current_url = driver.current_url
          next_anchor.click()
          WebDriverWait(driver, 10).until(EC.url_changes(current_url))
        except TimeoutException as e:
          self.logger.error(f"Error trying to access the next page. {e}")

    def retrieve_news(self, params: dict) -> List[List[str]]:
        """
        Retrieves news articles from the Los Angeles Times website based on specified parameters.

        Parameters:
        params (dict): A dictionary containing the query, section, and months parameters for filtering the news articles.

        Returns:
        List[List[str]]: A list of news articles, where each article is represented as a list containing the title, description, date, image path, query count, and money mention status.
        """
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
