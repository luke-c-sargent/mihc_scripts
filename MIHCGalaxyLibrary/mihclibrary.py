from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from bioblend.galaxy import libraries


class MIHCGalaxyLibrary(MIHCBase):
  """Abstract out Galaxy library interactions required for MIHC analysis"""

  LIBRARY_KEYS = [
    "name", "id", "description"
  ]

  DEFAULT_LIBRARY_NAME = "mIHC Sample Data Repository"
  DEFAULT_LIBRARY_DESCRIPTION = "the data library for mIHC sample data"

  def __init__(self, galaxy_instance, lib_name=None, lib_description=None):
    # configure defaults
    if not lib_name:
      self.name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    else:
      self.name = lib_name
    if not lib_description:
      self.description = MIHCGalaxyLibrary.DEFAULT_LIBRARY_DESCRIPTION
    else:
      self.description = lib_description

    # initialize bioblend Library object
    self._lib = libraries.LibraryClient(galaxy_instance)

    # get library info, create if needed, error if multiple libraries found
    _lib = self._get_lib()
    if not _lib:
      _lib = self._create_lib()
    self.__dict__.update(_lib)
    self._update_contents()

  # content keys: url, id, name, type
  def _update_contents(self):
    """ check remote library's contents, update class's contents variable"""
    self.library_contents = self._lib.show_library(self.id, contents=True)

  def _get_lib(self):
    self.dbg("checking for library {}".format(self._lib))
    _temp_r = self._lib.get_libraries(name=self.name)
    _r = []
    for _ in _temp_r:
      if (_['deleted']):
        continue
      _r.append(_)
    if len(_r) > 1:
      self.err("there should be exactly one repo named {}.... {} found.".format(self.name, len(_r)))
    elif len(_r) == 0:
      return None
    else:
      return _r[0]

  def _create_lib(self):
    self.dbg("creating library {}".format(self.name))
    return self._lib.create_library(self.name, self.description)

  def _create_lib_folder(self, folder_name):
    # ensure it doesn't already exist
    for _f in self.library_contents:
      if _f['type'] == 'folder':
        if _f['name'].split('/')[-1] == folder_name:
          self.dbg("folder {} already exists in library {}, skipping creation".format(folder_name, self.id))
          return _f
    self.dbg("creating library folder {} in library id={}".format(folder_name, self.id))
    _r = self._lib.create_folder(self.id, folder_name, description="Sample {}".format(folder_name))
    if type(_r) == list and len(_r) == 1:
      _r = _r[0]
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
    """Helper function for single datasets"""
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

  def get_file_id(self, filename):
    _rs = []
    for _f in self.library_contents:
      if _f["type"] == "file" and filename in _f["name"]:
        _rs.append(_f["id"])
    if not _rs:
      self.err("{} file not found in library".format(filename))
      return {}
    elif len(_rs) != 1:
      self.err("files found matching name {} > 1".format(filename))
    return _rs[0]

  # for pretty printing, when necessary
  def __repr__(self):
    _s = "<MIHCGalaxyLibrary>\n"
    for _k in MIHCGalaxyLibrary.LIBRARY_KEYS:
      _s += "  '{}': '{}'\n".format(_k, self.__dict__[_k])
    if self.library_contents:
      _s += "  'library_contents':\n"
      for _k in self.library_contents:
        _s += "  - '{}'\n".format(_k)
    return _s + "</MIHCGalaxyLibrary>"