from MIHCBase import MIHCBase
from bioblend.galaxy import histories
from datetime import datetime

class MIHCHistory(MIHCBase):
  
  KEYS = [
    'name', 'id', 'items'
  ]
  
  
  
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
      self.dbg("Created history:\n{}"0.format(_info))
      self._data = _info
    else:
      self.err("Need either a name to create a new history or an id to find existent")

  def add_data(self, dataset):
    # for every dataset element, determine if its a list or a string
      # add dataset if its a simple string
      # add dataset collection if it's a list
    raise Exception("IMPLEMENT ME PLEASE")

  def _add_dataset(self, data):
    return self._hist.upload_dataset_from_library(self._data["id"], lib_dataset_id)
    
  def _add_dataset_collection():
    raise Exception("IMPLEMENT ME PLEASE")
