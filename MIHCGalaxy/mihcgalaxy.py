import argparse
import json

from datetime import datetime

from bioblend.galaxy import GalaxyInstance, libraries, histories

from MIHCBase import MIHCBase
from MIHCGalaxyLibrary import MIHCGalaxyLibrary
from MIHCHistory import MIHCHistory

class MIHCGalaxy(MIHCBase):
  
  def __init__(self, galaxy_address, api_key, samples, lib_name=None):
    if not lib_name:
      lib_name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    self._gi = GalaxyInstance(url=galaxy_address, key=api_key)
    self._lib = MIHCGalaxyLibrary(self._gi, lib_name)
    self._hists = []
    _rs = []
    # samples = dict of MIHCData objects 
    # K: V == source directory: MIHCDataset Object
    for _s in samples: # each sample needs:
      # a history
      _hname = samples[_s].get_data()["source_dir"].split('/')[-1]
      _h = MIHCHistory(name=_hname, galaxy_instance=self._gi)
      # that history, populated
      _h.add_data(samples[_s])
      # a workflow invoked against that history
      #collect results
asdffdaasdffdaasdf
