import json
from os import listdir,getcwd
from os.path import isfile, isdir
from ..MIHCBase import MIHCBase
from ..MIHCDataset import MIHCDataset

class Detector(MIHCBase):
  
  def __init__(self, location=None, print=False):
    if location:
      if isdir(location):
        self.ROOT = location
      else:
         self.err("'{}' is not a valid directory".format(location))
    else:
      self.ROOT = getcwd()
    self._data = self._find_mihc_data(self.ROOT)

  def _is_mihc_folder(self, location, exclude_processed=True):
    _files, _dirs = self._list_dir(location)
    _result = {
      "images" : [],
      "nuclei" : "",
      "annotation" : "",
      "parent_workflow": "",
      "cppipe": ""
    }

    if exclude_processed:
      if "Processed" in _dirs:
        return {}
      
    for f in _files:
      if f[-3:] == "xml":
        self.dbg("found xml file {}".format(f))
        _result["annotation"] = f
        # xml present, is complementary .svs also present?
        if str(f[:-3] + "svs") not in _files:
           self.err("ERROR: missing required nuclei image file: \n\t-[{}]".format(f[:-3] + "svs"))
        else:
          self.dbg("adding nuclei file {}".format(f[:-3] + "svs"))
          _result["nuclei"] = f[:-3] + "svs"
      elif f[-6:] == "cppipe":
        _result["cppipe"] = f
      elif f[-3:] == "svs":
        _result["images"].append(f)
    # remove nuclei file from images
    if _result["nuclei"] in _result["images"]:
      _result["images"].remove(_result["nuclei"])
    # find parent workflow, remove trailing '/'
    _l = location if location[-1] != '/' else location[:-1]
    parent_dir = '/'.join(_l.split('/')[:-1])
    _files, _dirs = self._list_dir(parent_dir)
    _wf = ""
    for f in _files:
      if f[-3:] == ".ga":
        if not _wf:
          _wf = f
        else:
          self.dbg("Multiple workflows found where one was expected:\n\t{} and {}... quitting.".format(_wf, f))
          return {}
    if _wf:
      _result["parent_workflow"] = _wf
    else:
      self.dbg("No workflows found in parent directory {}... can't process".format(parent_dir))
      return {}
    for _k in _result:
      if not _result[_k]:
        self.dbg("Missing required input: {}".format(_k))
        return {}
    return _result

  def _list_dir(self, location):
    self.dbg("listing location {}".format(location))
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
        self.dbg("object '{}' is weird... skipping".format(c))
    self.dbg("listing result: \nFILES: {}\nDIR: {}".format(_files, _dir))
    return (_files, _dirs)

  def _find_mihc_data(self, location):
    self.dbg("looking in {}....".format(location))
    possible_locations = [location]
    results = []
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
        results.append((_loc, _mihc))
      else:
        self.dbg("its not mihc")
        possible_locations.extend(self._list_dir(_loc)[1])
        self.dbg(possible_locations)
    return results

  def get_data(self):
    return self._data
