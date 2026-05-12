import logging
import sys
import os
from datetime import datetime

def setup_logger(name="ev_intelligence"):
    """
    Creates logger for the app.
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Make logs folder if needed
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Make logs look nice
    format_str = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    formatter = logging.Formatter(format_str)
    
    # Console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File output
    log_filename = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger we can use anywhere
logger = setup_logger()
