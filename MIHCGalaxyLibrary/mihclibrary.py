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
      self.name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    else:
      self.name = lib_name
    if not lib_description:
      self.description = MIHCGalaxyLibrary.DEFAULT_LIBRARY_DESCRIPTION
    else:
      self.description = lib_description
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


  # content keys: url, id, name, type
  def _update_contents(self):
    self.library_contents = self._lib.show_library(self.id, contents=True)
    #for _lc in self.library_contents:
     # print(_lc)

  def _get_lib(self):
    self.dbg("checking for library {}".format(self._lib))
    _r = self._lib.get_libraries(name=self.name)
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
    # ensure it doesn't already exist
    for _f in self.library_contents:
      if _f['type'] == 'folder':
        if _f['name'].split('/')[-1] == folder_name:
          self.dbg("folder {} already exists in library {}, skipping creation".format(folder_name, self.id))
          return _f
    self.dbg("creating library folder {} in library id={}".format(folder_name, self.id))
    _r = self._lib.create_folder(self.id, folder_name, description="Sample {}".format(folder_name))
    self._update_contents()
    return _r
  
  def _upload_file_to_dir(self, paths, folder_id):
    _r = None
    if paths:
      _r = self._lib.upload_from_galaxy_filesystem(self.id, paths, folder_id, link_data_only="link_to_files")
      self._update_contents()
    return _r

  def add_mihc_datasets(self, datasets):
    # in case its just one dataset
    _r = []
    if not isinstance(datasets, list):
      datasets = [datasets]
    for _d in datasets:
      _rd = self._add_mihc_dataset(_d)
      if _rd:
        _r.append(_rd)
    return _r

  def _add_mihc_dataset(self, dataset):
    _files = dataset._get_files_to_upload(self)
    if not _files:
      self.warn("Files already present in Data Library")
      return []
    end_folder = dataset._data["source_dir"].split('/')[-1]
    # create library folder
    _folder_info = self._create_lib_folder(end_folder)
    # 'paths' string creation helper fn

    def _unify_paths(*args):
      final_string = ""
      for _a in args:
        if isinstance(_a, list):
          for _elem in _a:
            final_string += "{}\n".format(_elem)
        else:
          final_string += "{}\n".format(_a)
      return final_string[:-1]
    
    # add files to created directory
    _r = self._upload_file_to_dir( _unify_paths(_files), _folder_info['id'] )
    dataset.in_library = True
    return _r
