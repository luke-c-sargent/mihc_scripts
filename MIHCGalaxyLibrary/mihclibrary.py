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
  
  def _upload_file_to_dir(self, paths, folder_id):
    if paths:
      self._lib.upload_from_galaxy_filesystem(lib_id, paths, folder_id, link_data_only="link_to_files")
      self._update_contents()
    else:
      return None

  def add_mihc_datasets(self, datasets):
    # in case its just one dataset
    if not isinstance(datasets, list):
      datasets = [datasets]
    for _d in datasets:
      self._add_mihc_dataset(_d)
      
  def _add_mihc_dataset(self, dataset):
    _files = dataset.get_files_to_upload()
    for _f in _files:
      pass
    
    


  # def _process_sample(self, sample):
  #   end_folder = list(sample.keys())[0].split('/')[-1]
  #   # is this folder present?
  #   lib_folders = [x for x in self.library_contents if x['type'] == 'folder']
  #   _r = {}
  #   for _f in lib_folders:
  #     if _f["name"] == str("/" + end_folder):
  #       self.dbg("folder '{}' already exists in data library '{}'".format(_f["name"], self.id))
  #       _r = _f
  #       break
  #   # its not, create
  #   if not _r:
  #     _r = self._create_lib_folder(self.id, end_folder)[0]
  #   _folder_id = _r["id"]
  #   _present_files = []
  #   for _pf in self.library_contents:
  #     if _pf["type"] != "file":
  #       continue
  #     _n = _pf['name'].split('/')
  #     if _n[1] == end_folder:
  #       _present_files.append(_n[-1])
  #   # add data
  #   _samples = sample[list(sample.keys())[0]]
  # 
  #   def absence(_sample, extant=_present_files):
  #       if _sample.split('/')[-1] in extant:
  #         return False
  #       return _sample
  # 
  #   _nuclei = absence(_samples["nuclei"])
  #   _images = _samples["images"]
  #   _image_string = ""
  #   for _i in _images:
  #     _sample = absence(_i)
  #     if _sample:
  #       _image_string = _image_string + "{}\n".format(_i)
  #   _annot  = absence(_samples["annotation"])
  #   print(_nuclei)
  #   print(_annot)
  #   print(_image_string)
  # 
  #   _result_info = []
  #   for _in in (_nuclei, _annot, _image_string):
  #     if _in:
  #       _r = upload_file_to_dir(lib_id, _in, _folder_id)
  #       if _r:
  #         _result_info.append(_r)
  #   return _result_info
