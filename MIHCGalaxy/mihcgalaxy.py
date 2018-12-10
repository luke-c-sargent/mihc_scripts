import argparse
import json

from datetime import datetime

from bioblend.galaxy import GalaxyInstance, libraries, histories

from MIHCBase import MIHCBase

class MIHCGalaxy(MIHCBase):
  
  DEFAULT_LIBRARY_NAME="mIHC Sample Data Repository"
  
  def __init__(self, galaxy_address, api_key, samples, lib_name=self.DEFAULT_LIBRARY_NAME):
    self._gi = GalaxyInstance(url=galaxy_address, key=api_key)
    self._lib = MIHCGalaxyLibrary(self._gi, lib_name)
    self._hist = histories.HistoryClient(self._gi)
    self._lib_name = lib_name

  def _get_lib(self, lib_name=LIBRARY_NAME):
    self.dbg("checking for library {}".format(lib_name))
    _r = lib.get_libraries(name=lib_name)
    if len(_r) > 1:
      raise Exception("there should be exactly one repo named {}.... {} found.".format(LIBRARY_NAME, len(_r)))
    elif len(_r) == 0:
      return None
    else:
      return _r[0]
