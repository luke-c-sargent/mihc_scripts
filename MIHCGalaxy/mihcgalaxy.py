import argparse
import json

from datetime import datetime

from bioblend.galaxy import GalaxyInstance, libraries, histories

from ..MIHCBase import MIHCBase
from ..MIHCGalaxyLibrary import MIHCGalaxyLibrary
from ..MIHCHistory import MIHCHistory

class MIHCGalaxy(MIHCBase):
  
  def __init__(self, galaxy_address, api_key, samples, lib_name=None):
    if not lib_name:
      lib_name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    self._gi = GalaxyInstance(url=galaxy_address, key=api_key)
    self._lib = MIHCGalaxyLibrary(self._gi, lib_name)