from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from mihc_scripts.Detector.detector import Detector
from mihc_scripts.MIHCGalaxy.mihcgalaxy import MIHCGalaxy

class MIHCRunner(MIHCBase):
  def __init__(self, location=None, api_key=None, galaxy_address=None, galaxy_port=None):
    # checking input
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
    self.galaxy = MIHCGalaxy(galaxy_address="{}:{}".format(galaxy_address, galaxy_port), api_key=api_key, samples=_samps)
