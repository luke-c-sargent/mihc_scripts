from .MIHCBase import MIHCBase
from .MIHCGalaxy import MIHCGalaxy
from .MIHCDataset import BaseMIHCData, MIHCFullRun
from .MIHCGalaxyLibrary import MIHCGalaxyLibrary
from .Detector import Detector
from .MIHCRunner import MIHCRunner

def run_mihc(location, key, address, port):
  mihcrun = MIHCRunner(location, key, address, port)
