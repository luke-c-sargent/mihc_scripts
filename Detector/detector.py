import json
from os import listdir,getcwd
from os.path import isfile, isdir

class Detector(MIHCBase):
  ROOT = ""
  
  def __init__(self, location=None, print=False, debug=False):
    if location:
      if isdir(location):
        self.ROOT = location
      else:
        err("'{}' is not a valid directory".format(location))
    else:
      self.ROOT = getcwd()
    _process_root(self.ROOT)

  def _is_mihc_folder(location, exclude_processed=True):
    _files, _dirs = list_dir(location)
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
        dbg("found xml file {}".format(f))
        _result["annotation"] = f
        # xml present, is complementary .svs also present?
        if str(f[:-3] + "svs") not in _files:
          err("ERROR: missing required nuclei image file: \n\t-[{}]".format(f[:-3] + "svs"))
        else:
          dbg("adding nuclei file {}".format(f[:-3] + "svs"))
          _result["nuclei"] = f[:-3] + "svs"
      elif f[-6:] == "cppipe":
        _result["cppipe"] = f
      elif f[-3:] == "svs":
        _result["images"].append(f)
    # remove nuclei file from images
    _result["images"].remove(_result["nuclei"])
    # find parent workflow, remove trailing '/'
    _l = location if location[-1] != '/' else location[:-1]
    parent_dir = '/'.join(_l.split('/')[:-1])
    _files, _dirs = list_dir(parent_dir)
    _wf = ""
    for f in _files:
      if f[-3:] == ".ga":
        if not _wf:
          _wf = f
        else:
          dbg("Multiple workflows found where one was expected:\n\t{} and {}... quitting.".format(_wf, f))
          return {}
    if _wf:
      _result["parent_workflow"] = _wf
    else:
      dbg("No workflows found in parent directory {}... can't process".format(parent_dir))
      return {}
    for _k in _result:
      if not _result[_k]:
        dbg("Missing required input: {}".format(_k))
        return {}
    return _result
