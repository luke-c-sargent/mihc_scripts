from MIHCDataset import BaseMIHCData

class MIHCDataset(BaseMIHCData):

  def __init__(self, source, library):
    self.in_library = False
    self.library = library

    # set data
    self._data = self.check_data(source)
    self._library_sync()

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

  def _library_sync(self):
    self.dbg("adding dataset to library {}:\n{}".format(self.library.name, self))
    if self.library and not self.in_library:
      _r = self.library._add_mihc_dataset(self)
    if _r:
      self.in_library = True
      return _r
    else:
      self.err("failure to upload dataset to library {}:\n{}".format(self.library.name, self))
      return None

  # def _validate(self, src):
  #   if isinstance(src, list):
  #     bad_files = []
  #     for _s in src:
  #       if not isfile(_s):
  #         bad_files.append(_s)
  #     if bad_files:
  #       error_string = "Error: the following provided files do not exist:\n"
  #       for _bf in bad_files:
  #         error_string += "  - {}\n".format(_bf)
  #       self.err(error_string)
  #       return False
  #     return True
  #   else:
  #     if not isfile(src):
  #       self.err("Error: provided file '{}' does not exist".format(src))
  #       return False
  #     return True

  # def get_data(self):
  #   return self.__dict__

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
            
