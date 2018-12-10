from MIHCBase import MIHCBase
from bioblend.galaxy import libraries


class MIHCGalaxyLibrary(MIHCBase):
  def __init__(self, galaxy_instance, library_name):
    self._name = library_name
    self._lib = libraries.LibraryClient(galaxy_instance)
    # get lib info, create if needed, error if multiples
    _lib = _get_lib()
    if _lib:
      print(_lib)
    else:
      pass
      # create 

  def _get_lib(self):
    self.dbg("checking for library {}".format(self._lib))
    _r = lib.get_libraries(name=self._name)
    if len(_r) > 1:
      self.err("there should be exactly one repo named {}.... {} found.".format(LIBRARY_NAME, len(_r)))
    elif len(_r) == 0:
      return None
    else:
      return _r[0]
