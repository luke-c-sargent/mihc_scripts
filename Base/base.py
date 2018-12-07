import logging
import sys

class MIHCBase:
  def __init__(self):
    pass
  
  def err(msg):
    logging.error(msg)
    sys.exit(1)

  def warn(msg):
    logging.warning(msg)
    
  def info(msg):
    logging.info(msg)

  def dbg(msg):
    logging.debug(msg)
