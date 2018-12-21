from MIHCBase import MIHCBase
from bioblend.galaxy import histories
from datetime import datetime

class MIHCHistory(MIHCBase):
  
  KEYS = [
    'name', 'id', 'items'
  ]
  
  @staticmethod
  def _extract_file_and_folder(full_path):
    _split = full_path.split('/')
    return _split[-1], _split[-2]
  
  def __init__(self, name=None, galaxy_instance=None, id=None, check_by="id", timestamp_new=True):
    self._hist = histories.HistoryClient(galaxy_instance)
    self._data = None
    self._datasets = []
    self._dataset_collections = []
    if id:
      # check if its already created
      raise Exception("Not yet implemented")
    elif name:
      # theres a name
      nonce=""
      if timestamp_new:
        nonce=str(datetime.utcnow()).split('.')[0]
        name += " @ {}".format(nonce)
      _info = self._hist.create_history(name=name)
      self.dbg("Created history:\n{}".format(_info))
      self._data = _info
    else:
      self.err("Need either a name to create a new history or an id to find existent")

  def add_data(self, dataset, library):
    _elements = dataset.get_files()
    # for every dataset element, determine if its a list or a string
    for _e in _elements:
      _val = _elements[_e]
      # add dataset if its a simple string
      if isinstance(_val, str):
        self._datasets.append(self._add_dataset(_val, library))
      # add dataset collection if it's a list
      elif isinstance(_val, list):
        self._dataset_collections.append(self._add_dataset_collection(_val, library))
      else:
        self.err("Dataset has weird file {} whose type {} is strange".format(_e, type(_val)))

  def get_dataset_info(self):
    return {
      "datasets": self._datasets,
      "dataset_collections": self._dataset_collections
    }

  def _add_dataset(self, data, library):
    _fname, _srcpath = MIHCHistory._extract_file_and_folder(data)
    _file_id = library.get_file_id(_fname, _srcpath)
    return self._hist.upload_dataset_from_library(self._data["id"], _file_id)
    
  def _add_dataset_collection(self, data, library):
    _e_ids = []
    for _datum in data:
      _fname, _srcpath = MIHCHistory._extract_file_and_folder(_datum)
      _file_id = library.get_file_id(_fname, _srcpath)
      _e = {
        "id": _file_id,
        "name": _fname,
        "src":"ldda"
      }
      _e_ids.append(_e)
    _description = {
      "collection_type": "list",
      "element_identifiers": _e_ids,
      "name": "Marker Image set"
    }
    return self._hist.create_dataset_collection(self._data["id"], _description)

  def run_wflow()
