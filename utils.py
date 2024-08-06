import re

def count_query(query: str, title: str, desc: str) -> int:
    """Count occurrences of the query in title and description."""
    occurr_title = re.findall(query, title)
    occurr_desc = re.findall(query, desc)
    count = len(occurr_title) + len(occurr_desc)
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
    return match is not None