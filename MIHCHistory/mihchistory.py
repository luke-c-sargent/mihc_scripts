from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from bioblend.galaxy import histories
from datetime import datetime

class MIHCHistory(MIHCBase):
  """Abstract out Galaxy History interactions required for MIHC analysis"""

  KEYS = [
    'name', 'id', 'items'
  ]

  @staticmethod
  def _extract_file_and_folder(full_path):
    _split = full_path.split('/')
    return _split[-1], _split[-2]

  def __init__(self, name=None, galaxy_instance=None, id=None, check_by="id", timestamp_new=True):
    # initialize bioblend History client
    self._hist = histories.HistoryClient(galaxy_instance)
    self._data = None
    self._datasets = []
    self._dataset_collections = []
    if id:
      # check if its already created
      raise Exception("Not implemented") # this should not happen
    elif name:
      # create unique string from name + date/time
      nonce=""
      if timestamp_new:
        nonce=str(datetime.utcnow()).split('.')[0]
        name += " @ {}".format(nonce)
      _info = self._hist.create_history(name=name)
      self.dbg("Created history:\n{}".format(_info))
      self._data = _info
    else:
      self.err("Need either a name to create a new history or an id to find existent")

  def get_id(self):
    return self._data["id"]

  def get_status(self):
    return self._hist.get_status(self._data["id"])

  def get_current_info(self):
    return self._hist.get_histories(history_id = self._data["id"])

  def get_history_contents(self):
    return self._hist.show_history(history_id = self._data["id"], contents = True)

  def add_data(self, dataset, library):
    """Adds a datasets to this history"""
    _elements = dataset.get_files()
    parent_folder = dataset._data["source_dir"].split('/')[-1:][0]
    # for every dataset element, determine if its a list or a string
    for _e in _elements:
      _val = _elements[_e]
      # add dataset if its a simple string
      if isinstance(_val, str):
        self._datasets.append(self._add_dataset(_val, library, parent_folder))
      # add dataset collection if it's a list
      elif isinstance(_val, list):
        self._dataset_collections.append(self._add_dataset_collection(_val, library, parent_folder, _e))
      else:
        self.err("Dataset has weird file {} whose type {} is strange".format(_e, type(_val)))

  def get_dataset_info(self):
    return {
      "datasets": self._datasets,
      "dataset_collections": self._dataset_collections
    }

  def _add_dataset(self, data, library, folder=None):
    _fname, _srcpath = MIHCHistory._extract_file_and_folder(data)
    if folder:
      _srcpath = folder
    _file_id = library.get_file_id("/{}/{}".format(_srcpath, _fname))
    return self._hist.upload_dataset_from_library(self._data["id"], _file_id)

  def _add_dataset_collection(self, data, library, parent_folder, name="Image Set"):
    _e_ids = []
    for _datum in data:
      _fname, _srcpath = MIHCHistory._extract_file_and_folder(_datum)
      _fpath = "/{}/{}".format(parent_folder, _fname)
      _file_id = library.get_file_id(_path)
      _e = {
        "id": _file_id,
        "name": _fname,
        "src":"ldda"
      }
      _e_ids.append(_e)
    _description = {
      "collection_type": "list",
      "element_identifiers": _e_ids,
      "name": name
    }
    return self._hist.create_dataset_collection(self._data["id"], _description)