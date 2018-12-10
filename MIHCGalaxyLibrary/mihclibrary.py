from MIHCBase import MIHCBase
from bioblend.galaxy import libraries


class MIHCGalaxyLibrary(MIHCBase):
  
  LIBRARY_KEYS = [
    "name", "id", "description"
  ]
  
  DEFAULT_LIBRARY_NAME = "mIHC Sample Data Repository"
  DEFAULT_LIBRARY_DESCRIPTION = "the data library for mIHC sample data"
  
  def __init__(self, galaxy_instance, lib_name=None, lib_description=None):
    if not lib_name:
      self.name = self.DEFAULT_LIBRARY_NAME
    if not lib_description:
      self.description = self.DEFAULT_LIBRARY_DESCRIPTION
    self._lib = libraries.LibraryClient(galaxy_instance)
    # get lib info, create if needed, error if multiples
    _lib = self._get_lib()
    if not _lib:
      _lib = self._create_lib(self.name, self.description)
    self.__dict__.update(_lib)
    self._update_contents()

  def __repr__(self):
    _s = "<MIHCGalaxyLibrary>\n"
    for _k in MIHCGalaxyLibrary.LIBRARY_KEYS:
      _s += "  '{}': '{}'\n".format(_k, self.__dict__[_k])
    if self.library_contents:
      _s += "  'library_contents':\n"
      for _k in self.library_contents:
        _s += "  - '{}'\n".format(_k)
    return _s + "</MIHCGalaxyLibrary>"

  def _update_contents(self):
    self.library_contents = self._lib.show_library(self.id, contents=True)

  def _get_lib(self):
    self.dbg("checking for library {}".format(self._lib))
    _r = self._lib.get_libraries(name=self.__dict__["name"])
    if len(_r) > 1:
      self.err("there should be exactly one repo named {}.... {} found.".format(LIBRARY_NAME, len(_r)))
    elif len(_r) == 0:
      return None
    else:
      return _r[0]

  def _create_lib(self):
    self.dbg("creating library {}".format(lib_name))
    _n = self._lib.create_library(self._name, self._description)["name"]
    return self._get_lib(_n)

  def _create_lib_folder(self, folder_name):
    for _f in self.library_contents:
      if _f['type'] == 'folder':
        if _f['name'].split('/')[-1] == folder_name:
          self.dbg("folder {} already exists in library {}, skipping creation".format(folder_name, self.id))
          return _f
    self.dbg("creating library folder {} in library id={}".format(folder_name, self.id))
    _r = self._lib.create_folder(self.id, folder_name, description="Sample {}".format(folder_name))
    self._update_contents()
    return _r
  
