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
      if instanceof(_val, str):
        self._add_dataset(_val, library)
      # add dataset collection if it's a list
      elif instanceof(_val, list):
        pass
      else:
        self.err("Dataset has weird file {} whose type {} is strange".format(_e, type(_val)))
    #raise Exception("IMPLEMENT ME PLEASE")

  def _add_dataset(self, data, library):
    _fname, _srcpath = MIHCHistory._extract_file_and_folder(data)
    _file_id = library.get_file_id(_fname, _srcpath)
    return self._hist.upload_dataset_from_library(self._data["id"], _file_id)
    
  def _add_dataset_collection():
    raise Exception("IMPLEMENT ME PLEASE")
