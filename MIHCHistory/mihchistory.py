from MIHCBase import MIHCBase
from bioblend.galaxy import histories
from datetime import datetime

class MIHCHistory(MIHCBase):
  
  KEYS = [
    'name', 'id', 'items'
  ]
  
  
  
  def __init__(self, name=None, galaxy_instance=gi, id=None, check_by="id", timestamp_new=True):
    self._hist = histories.HistoryClient()
    if id:
      # check if its already created
      pass
    elif name:
      # theres a name
      nonce=""
      if timestamp_new:
        nonce=str(datetime.utcnow()).split('.')[0]
        name += " {}".format(nonce)
      _info = self._hist.create_history(name=name)
      self.dbg("Created history:\n{}".format(_info))
    else:
      self.err("Need either a name to create a new history or an id to find existent")
