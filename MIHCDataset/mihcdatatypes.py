from MIHCBase import MIHCBase
from workflows import workflows


from os.path import isfile, isdir

class BaseMIHCData(MIHCBase):
  
  CONTENTS = {} # MUST HAVE source_dir PATH AS ENTRY
  
  def _get_workflow(self):
    return workflows[self.__class__.__name__]
  
  def __init__(self, location=None, data=None):
    self._data = {}
    self.in_library = False
    if location:
      self._data["parent_workflow"] = self._get_workflow()
      self._data.extend(self.check_data(location))
    elif data:
      self._data = data
      if not self.validate():
        self.err("Error: invalid dataset:\n{}".format(self._data))
  
  def __repr__(self):
    _r = "<MIHCDataset>\n"
    for _k in self._data.keys():
      _r += "  {}:\n".format(_k)
      if isinstance(self._data[_k], list):
        for _i in self._data[_k]:
          _r += "\t{}\n".format(_i)
      else:
        _r += "\t{}\n".format(self._data[_k])
    _r +="</MIHCDataset>"
    return _r
    
  def library_sync(self, library):
    self.dbg("adding dataset to library {}:\n{}".format(library.name, self))
    if library and not self.in_library:
      _r = library._add_mihc_dataset(self)
    if _r:
      self.in_library = True
      return _r
    else:
      self.warn("Dataset upload to library {} not performed as all files present".format(library.name, self))
      return None
      
  def get_files(self):
    _r = dict(self._data)
    del _r["source_dir"]
    del _r["parent_workflow"]
    return _r

  def _get_files_to_upload(self, library):
    # was it already added?
    if self.in_library:
      return {}
    end_folder = self._data["source_dir"].split('/')[-1]
    # create a list of files in dataset
    _r = []
    for _key in self.CONTENTS:
      if _key in ["source_dir", "parent_workflow"]:
        continue
      _value = self._data[_key]
      if isinstance( _value, list):
        _r.extend(_value)
      else:
        _r.append(_value)
    # remove duplicates
    _r = list(set(_r))
    _r.sort()
    _fs = library.library_contents
    # for every object already in the library....
    for _f in _fs:
      if _f['type'] != 'file': # ignore non-files
        continue
      if "/{}/".format(end_folder) in _f['name']: # check to see if its in the folder
        _filename = _f['name'].split('/')[-1]
        # for every potential input:
        extant_files = []
        for _ds in _r:
          if _filename in _ds:
            extant_files.append(_ds)
        for _ef in extant_files:
          _r.remove(_ef)
    return _r

  @staticmethod
  def check_data(location):
    raise Exception("ABSTRACT MIHCDATA FUNCTION 'check_data' NOT DEFINED")
  
  def get_data(self):
    return self._data
  
  # ensure these files actually exist
  def validate(self):
    _d = self.get_data()
    for _k in _d:
      if not isinstance(_d[_k], self.CONTENTS[_k]):
        self.warn("data entry for {} is not of type {}".format(_k, self.CONTENTS[_k]))
        return False
      src = _d[_k]
      if isinstance(src, list):
        bad_files = []
        for _s in src:
          if not isfile(_s):
            bad_files.append(_s)
        if bad_files:
          error_string = "Error: the following provided files do not exist:\n"
          for _bf in bad_files:
            error_string += "  - {}\n".format(_bf)
          self.err(error_string)
          return False
        return True
      else:
        if not isfile(src):
          self.err("Error: provided file '{}' does not exist".format(src))
          return False
        return True

class MIHCFullRun(BaseMIHCData):
  
  CONTENTS = {
    "images": list,
    "nuclei": str,
    "annotation": str,
    "parent_workflow": str,
    "cppipe": str,
    "source_dir": str
  }
  
  @staticmethod
  def check_data(location):
    _files, _dirs = MIHCBase._list_dir(location)
    # easy out
    if "Processed" in _dirs:
      return {}

    _result = {
      "images" : [],
      "nuclei" : "",
      "annotation" : "",
      "cppipe": "",
      "source_dir": location
    }
    # data is: files
    # HAS: <name>.xml, <name>.svs, other svs's, cppipe file
    # DOESNT HAVE: 'processed' directory
    for f in _files:
      if f[-3:] == "xml":
        MIHCBase.dbg("found xml file {}".format(f))
        _result["annotation"] = f
        # xml present, is complementary .svs also present?
        if str(f[:-3] + "svs") not in _files:
           MIHCBase.dbg("FULL RUN DATASET: missing required nuclei image file: \n\t-[{}]".format(f[:-3] + "svs"))
           return {}
        else:
          MIHCBase.dbg("adding nuclei file {}".format(f[:-3] + "svs"))
          _result["nuclei"] = f[:-3] + "svs"
      elif f[-6:] == "cppipe":
        _result["cppipe"] = f
      elif f[-3:] == "svs":
        _result["images"].append(f)
    # remove nuclei file from images
    if _result["nuclei"] in _result["images"]:
      _result["images"].remove(_result["nuclei"])
    # find parent workflow, remove trailing '/'
    # _l = location if location[-1] != '/' else location[:-1]
    # parent_dir = '/'.join(_l.split('/')[:-1])
    # _files, _dirs = MIHCBase._list_dir(parent_dir)
    # _wf = ""
    # for f in _files:
    #   if f[-3:] == ".ga":
    #     if not _wf:
    #       _wf = f
    #     else:
    #       MIHCBase.dbg("Multiple workflows found where one was expected:\n\t{} and {}... quitting.".format(_wf, f))
    #       return {}
    # if _wf:
    #   _result["parent_workflow"] = _wf
    # else:
    #   MIHCBase.dbg("No workflows found in parent directory {}... can't process".format(parent_dir))
    #   return {}
    for _k in _result:
      if not _result[_k]:
        MIHCBase.warn("Missing required input: {}".format(_k))
        return {}
    return _result

    
