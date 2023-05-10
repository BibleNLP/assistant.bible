'''Sets the logging path and other related settings'''

import os
import logging
from logging.handlers import RotatingFileHandler

# Define and configure logger so that all other modules can use it
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("LOGGING_LEVEL", "DEBUG"))
handler = RotatingFileHandler('../logs/assistant_dot_bible.log', maxBytes=10000000, backupCount=10)
fmt = logging.Formatter(fmt='%(asctime)s|%(filename)s:%(lineno)d|%(levelname)-8s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
log.addHandler(handler)
