import re
import logging
from config import LOG_FILE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
stream_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

def count_query(query: str, title: str, desc: str) -> int:
  """
    Count occurrences of the query in the title and description.

    This function counts how many times the specified query appears in both
    the title and description by using regular expression matching.

    Parameters:
    query (str): The query string to search for.
    title (str): The title string to search within.
    desc (str): The description string to search within.

    Returns:
    int: The total number of occurrences of the query in the title and description.
  """
  occurr_title = re.findall(query, title)
  occurr_desc = re.findall(query, desc)
  count = len(occurr_title) + len(occurr_desc)
  logger.debug(f"Query '{query}' found {count} times in title and description.")
  return count


def mentions_money(text: str) -> bool:
  """
    Check if the text mentions money.

    This function checks whether the given text contains any mention of monetary values
    using a regular expression pattern that matches common money formats.

    Parameters:
    text (str): The text to check for monetary mentions.

    Returns:
    bool: True if the text mentions money, False otherwise.
  """
  pattern = r"""
    (?<!\w)  
    (                 
    \$\d{1,3}(,\d{3})*(\.\d{2})? | 
    \d+(\.\d{1,2})?\s?(dollars|USD)
    )                 
    (?!\w)  
  """
  match = re.search(pattern, text, re.VERBOSE | re.IGNORECASE)
  logger.debug(f"Text '{text}' mentions money: {match is not None}")
  return match is not None

def normalize_str(text: str) -> str:
  """
    Normalize the text by removing any kind of punctuation.

    This function removes all non-alphanumeric characters (excluding spaces) from the given text,
    effectively normalizing it by retaining only letters, numbers, and whitespace.

    Parameters:
    text (str): The text to be normalized.

    Returns:
    str: The normalized text with punctuation removed.
  """

  return re.sub(r'[^a-zA-Z0-9\s]', '', text)