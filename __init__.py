from .MIHCBase import MIHCBase
from .MIHCGalaxy import MIHCGalaxy
from .MIHCDataset import MIHCDataset
from .MIHCGalaxyLibrary import MIHCGalaxyLibrary
from .Detector import Detector

class MIHC_Runner(MIHCBase):
  def __init__(self, location=None, api_key=None, galaxy_address=None, galaxy_port=None):
    if not api_key:
      self.err("API key is required")
    if not galaxy_address:
      galaxy_address = "localhost"
      self.warn("No Galaxy address provided -- using {}".format(galaxy_address))
    if not galaxy_port:
      galaxy_port = "8088"
      self.warn("No Galaxy port provided -- using {}".format(galaxy_port))
    # sense the samples
    self.detector = Detector(location=location)
    # provision galaxy instance with discovered samples
    _samps = self.detector.get_data()
    self.galaxy = MIHCGalaxy(galaxy_address=galaxy_address, api_key=api_key, samples=_samps)
    # create MIHCDatasets
    # ACTUALLY I SHOULD PROBABLY SEND THIS TO MIHCGalaxy
    _mihc_datasets = []
    
    for _loc in _samps:
      _data = _samps[_loc] # [images], nuclei, annotation, cppipe, parent_workflow
      _mihc_datasets.append(MIHCDataset(_loc, ))
    # ***************************^^^^^^^^^^^^^^^^^^^^^^**********************
    
