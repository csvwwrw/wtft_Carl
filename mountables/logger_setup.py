import logging
from logging.handlers import TimedRotatingFileHandler
import re

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno == self.__level
    
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def double_logger_setup(main_filename, error_filename, logger):

    logger.setLevel(logging.INFO)
    folder = main_filename.replace(".log", "_logs")
    
    if (logger.hasHandlers()):
        logger.handlers.clear()
        
    h1 = TimedRotatingFileHandler(f'mountables/{folder}/{main_filename}', when = 'midnight', backupCount = 7)
    h1.addFilter(MyFilter(logging.INFO))
    h1.suffix = "%Y%m%d"
    h1.extMatch = re.compile(r"^\d{8}$") 
    h1.setFormatter(formatter)
    logger.addHandler(h1)
    
    
    h2 = TimedRotatingFileHandler(f'mountables/{folder}/{error_filename}', when = 'midnight', backupCount = 7)
    h2.addFilter(MyFilter(logging.ERROR))
    h2.suffix = "%Y%m%d"
    h2.extMatch = re.compile(r"^\d{8}$") 
    h2.setFormatter(formatter)
    logger.addHandler(h2)