import re
from base_logger import BaseLogger

class Utils(BaseLogger):
  """
  The Utils class provides utility functions for processing and analyzing text data, 
  including counting occurrences of a query, checking for mentions of money, and normalizing text.

  This class inherits from BaseLogger to provide logging capabilities for debugging and tracking purposes.
  """

  def __init__(self):
    super().__init__(logger_name=__name__)
  
  def count_query(self, query: str, title: str, desc: str) -> int:
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
    -1 if the query is empty.
    """
    if query == '':
      self.logger.debug(f"The query is empty, so the value of count will assume -1.")
      return -1
    
    occurr_title = re.findall(query.lower(), title.lower())
    occurr_desc = re.findall(query.lower(), desc.lower())
    count = len(occurr_title) + len(occurr_desc)

    self.logger.debug(f"Query '{query}' found {count} times in title and description.")
    return count

  def mentions_money(self, text: str) -> bool:
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
    self.logger.debug(f"Text '{text}' mentions money: {match is not None}")
    return match is not None

  def normalize_str(self, text: str) -> str:
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