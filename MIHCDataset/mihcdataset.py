from os import listdir,getcwd
from os.path import isfile, isdir

class MIHCDataset(MIHCBase):
  
  KEY_WHITELIST = ["nuclei", "images", "annotation", "cppipe", "parent_workflow"]
  
  def __init__(self, **kwargs):
    for _k in kwargs:
      if _k not in KEY_WHITELIST or not validate(kwargs[_k]):
        del kwargs[_k]
    self.__dict__.update(kwargs)

  def _validate(src):
    if isinstance(src, list):
      bad_files = []
      for _s in src:
        if not isfile(_s):
          bad_files.append(_s)
      if bad_files:
        error_string = "Error: the following provided files do not exist:\n"
        for _bf in bad_files:
          error_string += "  - {}\n".format(_bf)
        err(error_string)
    else:
      if not isfile(src):
        err("Error: provided file '{}' does not exist".format(src))
      return True  
