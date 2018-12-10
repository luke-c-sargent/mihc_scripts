from os import listdir,getcwd
from os.path import isfile, isdir
from MIHCBase import MIHCBase

class MIHCDataset(MIHCBase):
  
  KEY_WHITELIST = ["nuclei", "images", "annotation", "cppipe", "parent_workflow"]
  
  def __init__(self, source, **kwargs):
    bad_args = []
    for _k in kwargs:
      if _k not in MIHCDataset.KEY_WHITELIST or not self._validate(kwargs[_k]):
        bad_args.append(_k)
        self.dbg("deleting {}".format(_k))
    for _ba in bad_args:
      del kwargs[_ba]
    kwargs['source_path'] = source
    self.__dict__.update(kwargs)

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

  def get_files_to_upload(self):
    _ys = [ self.__dict__[_y] for _y in self.KEY_WHITELIST ]
    return dict(zip(self.KEY_WHITELIST, _ys))
