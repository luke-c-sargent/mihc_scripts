from os import listdir,getcwd
from os.path import isfile, isdir
from MIHCBase import MIHCBase

class MIHCDataset(MIHCBase):
  
  KEY_WHITELIST = ["nuclei", "images", "annotation", "cppipe", "parent_workflow"]
  
  def __init__(self, source, library, **kwargs):
    self.in_library = False
    self.library = library
    bad_args = []
    for _k in kwargs:
      if _k not in MIHCDataset.KEY_WHITELIST or not self._validate(kwargs[_k]):
        bad_args.append(_k)
        self.dbg("deleting {}".format(_k))
    for _ba in bad_args:
      del kwargs[_ba]
    kwargs['source_path'] = source
    self.__dict__.update(kwargs)
    self._library_sync()

  def __repr__(self):
    _r = "<MIHCDataset>\n"
    for _k in self.__dict__.keys():
      _r += "  {}:\n".format(_k)
      if isinstance(self.__dict__[_k], list):
        for _i in self.__dict__[_k]:
          _r += "\t{}\n".format(_i)
      else:
        _r += "\t{}\n".format(self.__dict__[_k])
    _r +="</MIHCDataset>"
    return _r
      

  def _library_sync(self):
    self.dbg("adding dataset to library {}:\n{}".format(self.library.name, self))
    if self.library and not self.in_library:
      _r = self.library._add_mihc_dataset(self)
    print(_r)
    if _r:
      self.in_library = True
      return _r
    else:
      self.err("failure to upload dataset to library {}:\n{}".format(self.library.name, self))
      return None

  def _validate(self, src):
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

  def get_data(self):
    return self.__dict__

  def _get_files_to_upload(self):
    # was it already added?
    if self.in_library:
      return {}
    end_folder = self.source_path.split('/')[-1]
    # create a list of files in dataset
    _r = []
    for _key in self.KEY_WHITELIST:
      _value = self.__dict__[_key]
      if isinstance( _value, list):
        _r.extend(_value)
      else:
        _r.append(_value)
    # remove duplicates
    _r = list(set(_r))
    _r.sort()
    _fs = self.library.library_contents

    # for every object already in the library....
    for _f in _fs:
      if _f['type'] != 'file': # ignore non-files
        continue
      print("/{}/".format(end_folder))
      if "/{}/".format(end_folder) in _f['name']: # check to see if its in the folder
        _filename = _f['name'].split('/')[-1]
        # for every potential input:
        extant_files = []
        for _ds in _r:
          print("is {} in {}?".format(_filename, _ds))
          if _filename in _ds:
            extant_files.append(_ds)
        for _ef in extant_files:
          _r.remove(_ef)
    return _r
            
