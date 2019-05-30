import json
from os import listdir,getcwd
from os.path import isfile, isdir
from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from mihc_scripts.MIHCDataset.mihcdatatypes import MIHCFullRun


class Detector(MIHCBase):
  """Determines the type of sample set(s) recursively, given a source directory
  """
  # add validation classes here... see MIHCDataset/mihcdatatypes.py
  DATA_CLASSES = [ MIHCFullRun ]
  
  def __init__(self, location, print=False):
    # _find_mihc_data returns a dict of MIHCData objects:
    #   K: V == source directory: MIHCDataset
    self._data = self._find_mihc_data(self.ROOT)

  def _is_mihc_folder(self, location):
    """Checks if location is an MIHCDataset, returns data processor object if so"""
    _rs = []
    for _data_class in self.DATA_CLASSES:
      _r = _data_class.check_data(location)
      if _r:
        _rs.append(_data_class(location=location, data=_r))
    if not _rs:
      return {}
    if _rs and len(_rs) > 1:
      _errstr = ""
      for _r in _rs:
        _errstr += "\n - {}".format(_r.__name__)
      self.err("Error: {} was detected to be multiple dataset types:{}".format(location, _errstr))
    return _rs[0]

  def _find_mihc_data(self, location):
    """Recurses through directories looking for MIHC datasets
    """
    self.dbg("looking in {}....".format(location))
    possible_locations = [location]
    results = {}
    while possible_locations:
      self.dbg("possibles:\n{}".format(possible_locations))
      # pop the top entry
      _loc = possible_locations[0]
      self.dbg("checking {}...".format(_loc))
      possible_locations.remove(possible_locations[0])
      # check if out
      _mihc = self._is_mihc_folder(_loc)
      if _mihc:
        self.dbg("its mihc: {}".format(_mihc))
        results[_loc]= _mihc
      else:
        self.dbg("{} is not mihc".format(_loc))
        possible_locations.extend(self._list_dir(_loc)[1])
    return results

  def get_data(self):
    return self._data
