from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from mihc_scripts.Detector.detector import Detector
from mihc_scripts.MIHCGalaxy.mihcgalaxy import MIHCGalaxy

class MIHCRunner(MIHCBase):
  """Starts analyses on samples found at `location,` run by specified Galaxy"""
  def __init__(self, location=None, api_key=None, galaxy_address=None, galaxy_port=None):
    """initializes object with sample source location and Galaxy server details

    Args:
      location       (str): directory where recursive sample scanning starts
          - default: script execution directory
      api_key        (str): administrator API key for specified Galaxy instance
      galaxy_address (str): address of Galaxy instance where analysis will run
      galaxy_port    (str): port in which Galaxy is listening
          - default: 80
    """
    # checking input
    if not api_key:
      self.err("API key is required")
    if not galaxy_address:
      galaxy_address = "localhost"
      self.warn("No Galaxy address provided -- using {}".format(galaxy_address))
    if not galaxy_port:
      galaxy_port = "80"
      self.warn("No Galaxy port provided -- using {}".format(galaxy_port))

    # detect the samples and determine what workflow to use
    self.detector = Detector(location=location)

    # provision Galaxy instance with discovered samples
    _samps = self.detector.get_data()
    self.galaxy = MIHCGalaxy(galaxy_address="{}:{}".format(galaxy_address, galaxy_port), api_key=api_key, samples=_samps)