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
    """Count occurrences of the query in title and description."""
    occurr_title = re.findall(query, title)
    occurr_desc = re.findall(query, desc)
    count = len(occurr_title) + len(occurr_desc)
    logger.debug(f"Query '{query}' found {count} times in title and description.")
    return count


def mentions_money(text: str) -> bool:
    """Check if the text mentions money."""
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