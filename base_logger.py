import logging
from config import LOG_FILE

class BaseLogger:

  def __init__(self, logger_name : str):
    self.logger = self.setup_logger(logger_name)
    
  def setup_logger(self, logger_name : str) -> logging.Logger:
    """
    Sets up the logger for the class.

    Returns:
    logging.Logger: Configured logger instance.
    """
    try:
      logger = logging.getLogger(logger_name)
      logger.setLevel(logging.DEBUG)
      file_handler = logging.FileHandler(LOG_FILE)
      stream_handler = logging.StreamHandler()

      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      file_handler.setFormatter(formatter)
      stream_handler.setFormatter(formatter)

      logger.addHandler(file_handler)
      logger.addHandler(stream_handler)

    except Exception as e:
      self.logger.error(f"Error setting up the logger. {e}")

    return logger