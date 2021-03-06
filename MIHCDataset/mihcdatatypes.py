from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from . import workflows

from os.path import isfile, isdir

class BaseMIHCData(MIHCBase):
  """Base class to be used in creating MIHCData classes

  Note: Accepts either local workflow, or predefined workflow from workflows.py
  """
  CONTENTS = {} # MUST HAVE source_dir, parent_workflow PATH AS ENTRY

  def _get_dict_workflow(self):
    return workflows[self.__class__.__name__]

  def __init__(self, location=None, data=None):
    self._data = {}
    self.in_library = False
    if location:
      _loc = location
      if _loc[-1] == '/':
        _loc = _loc[:-1]
      _parent_dir = "/".join(_loc.split('/')[:-1])
      _files = self._list_dir(_parent_dir)[0]
      wfs = []
      cppipes = []
      for _f in _files:
        if _f[-3:] == ".ga":
          wfs.append(_f)
        elif _f[-7:] == ".cppipe":
          cppipes.append(_f)
      if len(wfs) > 1 or len(wfs) == 0:
        self.err("Require exactly 1 workflow; found {} in dir {}".format(len(wfs), _parent_dir))
      else:
        self._data["parent_workflow"] = wfs[0]
      if len(cppipes) > 1 or len(cppipes) == 0:
        self.err("Require exactly 1 cppipe file; found {} in dir {}".format(len(cppipes), _parent_dir))
      else:
        self._data["CP_PIPELINE"] = cppipes[0]

      #this component calls the subclass-specific check_data()
      self._data.update(self.check_data(location))
    elif (not location):
      self.err("Please provide location")

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
    """Ensure this dataset is either added to or already in the specified library"""
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
    """Get a list of sample files"""
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
    """Abstract detection function classes extending BaseMIHCData must implement"""
    raise Exception("ABSTRACT MIHCDATA FUNCTION 'check_data' NOT DEFINED")

  @classmethod
  def get_inputs(cls):
    _r = dict(cls.CONTENTS)
    for _val in ["parent_workflow", "source_dir"]:
      if _val in _r:
        del _r[_val]
    return _r

  def get_data(self):
    return self._data

  def validate(self):
    """Ensure that detected files exist"""
    _d = self.get_data()
    for _k in _d:
      if _k == "parent_workflow":
        continue
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
  """A Full MIHC workflow run"""
  CONTENTS = {
    "MARKER_COL": list,
    "TARGET_NUC": str,
    "ANNOT_XML": str,
    "parent_workflow": str,
    "CP_PIPELINE": str,
    "source_dir": str
  }

  @staticmethod
  def check_data(location):
    _files, _dirs = MIHCBase._list_dir(location)
    # quick out
    if "Processed" in _dirs:
      return {}

    _result = {
      "MARKER_COL" : [],
      "TARGET_NUC" : "",
      "ANNOT_XML" : "",
      "source_dir": location
    }
    # data is: files
    # HAS: <name>.xml, <name>.svs, other svs's, cppipe file
    # DOESNT HAVE: 'processed' directory
    for f in _files:
      if f[-3:] == "xml":
        MIHCBase.dbg("found xml file {}".format(f))
        _result["ANNOT_XML"] = f
        # xml present, is complementary .svs also present?
        if str(f[:-3] + "svs") not in _files:
           MIHCBase.dbg("FULL RUN DATASET: missing required nuclei image file: \n\t-[{}]".format(f[:-3] + "svs"))
           return {}
        else:
          MIHCBase.dbg("adding nuclei file {}".format(f[:-3] + "svs"))
          _result["TARGET_NUC"] = f[:-3] + "svs"
      elif f[-3:] == "svs":
        _result["MARKER_COL"].append(f)
    # remove nuclei file from images
    if _result["TARGET_NUC"] in _result["MARKER_COL"]:
      _result["MARKER_COL"].remove(_result["TARGET_NUC"])
    for _k in _result:
      if not _result[_k]:
        MIHCBase.warn("Missing required input: {}".format(_k))
        return {}
    # check for existent registered region files
    if "{}/Registered_Regions".format(location) in _dirs:
      _subdirs = MIHCBase._list_dir("{}/Registered_Regions".format(location))[1]
      for _subdir in _subdirs:
        _rr_files = [ _file for _file in MIHCBase._list_dir(_subdir)[0] if _file[-3:] == "tif" ]
        _result["MARKER_COL"].extend(_rr_files)
    return _result