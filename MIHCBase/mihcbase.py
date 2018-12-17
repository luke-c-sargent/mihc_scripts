import logging
import sys
from os import listdir
from os.path import isfile, isdir

class MIHCBase:
  def __init__(self):
    pass

  @staticmethod
  def err(msg, raise_e = False):
    if raise_e:
      logging.error(msg + " -- raising exception")
      raise Exception(msg)
    else:
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

  @staticmethod
  def _list_dir(location):
    MIHCBase.dbg("listing location {}".format(location))
    _files = []
    _dirs  = []
    _contents = listdir(location)
    for c in _contents:
      c = location + str("" if location[-1] == "/" else "/") + c
      if isfile(c):
        _files.append(c)
      elif isdir(c):
        _dirs.append(c)
      else:
        MIHCBase.dbg("object '{}' is weird... skipping".format(c))
    MIHCBase.dbg("listing result: \nFILES: {}\nDIR: {}".format(_files, _dirs))
    return (_files, _dirs)
