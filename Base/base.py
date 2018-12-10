import logging
import sys

class MIHCBase:
  def __init__(self):
    pass

  @staticmethod
  def err(msg):
    logging.error(msg)
    sys.exit(1)

  @staticmethod
  def warn(msg):
    logging.warning(msg)

  @staticmethod
  def info(msg):
    logging.info(msg)

  @staticmethod
  def dbg(msg):
    logging.debug(msg)
