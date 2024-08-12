# News Extractor Project

This project is designed to extract news articles from the Los Angeles Times website based on specified search parameters and save the extracted data into an Excel file and the images in .jpg files.

Table of Contents
- [News Extractor Project](#news-extractor-project)
- [Files](#files)
  - [tasks.py](#taskspy)
  - [utils.py](#utilspy)
  - [news\_retriever.py](#news_retrieverpy)
  - [task\_manager.py](#task_managerpy)
  - [base\_logger.py](#base_loggerpy)
  - [config.py](#configpy)
- [Installation](#installation)
- [Usage](#usage)
- [Logging](#logging)
- [License](#license)


# Files
## tasks.py

Contains the main task execution logic using the Robocorp @task decorator. It initializes the TaskManager and calls the extract_news method.

```py
from task_manager import TaskManager
from robocorp.tasks import task

@task
def execute_task():
  task_manager = TaskManager()
  task_manager.extract_news()

```
## utils.py

Provides utility functions for counting query occurrences, checking for monetary mentions, and normalizing strings. Inherits from BaseLogger for logging purposes.


```py
import re
from baselogger import BaseLogger

class Utils(BaseLogger):
  # Utility functions here
```

## news_retriever.py

Contains the NewsRetriever class, which handles web scraping using Selenium to extract news articles, download images, and apply filters based on search parameters. Inherits from BaseLogger for logging purposes.


```py
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from base_logger import BaseLogger
from utils import Utils
from config import OUTPUT_DIR

class NewsRetriever(BaseLogger):
  # News retrieval functions here
```
## task_manager.py

Defines the TaskManager class, which coordinates the overall task of extracting news articles and saving them to an Excel file. Inherits from BaseLogger for logging purposes.

```py
from utils import Utils
from news_retriever import NewsRetriever
from base_logger import BaseLogger
from robocorp import workitems

class TaskManager(BaseLogger):
  # Task management functions here
```

## base_logger.py

Defines the BaseLogger class for setting up logging configurations used by other classes in the project.

```py
import logging
from config import LOG_FILE

class BaseLogger:
  # Logger setup functions here
```

## config.py
Contains configuration settings such as the output directory and log file path.

```py
OUTPUT_DIR = 'output'
LOG_FILE = 'output/news_extractor.log'
```

# Installation

Clone the repository:


```sh
git clone https://github.com/yourusername/news-extractor.git
cd news-extractor
```

# Usage

Install the Robocorp VS Code extensions:

- Open Visual Studio Code.
  - Go to the Extensions view by clicking the Extensions icon in the Activity Bar on the side of the window.
  - Search for "Robocorp" and install the following extensions:
    - Robocorp Code
    - Robocorp Log
    - Robocorp Inspector
- Open the project folder in VS Code:
  - Click on "File" in the top menu, then select "Open Folder..."
  - Navigate to the `news-extractor` folder and click "Select Folder".

- Run the task:
  - In the VS Code sidebar, click on the Robocorp icon.
  - Under "Tasks", you should see `LA Times Extraction`.
  - Click on `Run Task` to run the task.

# Logging
Logging is configured in the `base_logger.py` file and is used across various modules to log information, errors, and debugging messages. The log file path is specified in config.py.

# License
This project is licensed under the Apache License. See the LICENSE file for more details.

