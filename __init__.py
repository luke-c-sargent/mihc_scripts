import yaml
import os

from mihc_scripts.MIHCRunner.mihcrunner import MIHCRunner
from mihc_scripts.MIHCBase.mihcbase import MIHCBase

def run_mihc(location=None, key=None, address=None, port=None):
  """Run MIHC Workflows

  Arguments:
  location:  the source directory to scan recursively
  key:       API key for the Galaxy instance target
  address:   IP address of Galaxy server
  port:      Galaxy port

  """
  config_file_name = "galaxy_settings.yml"
  config_to_args_mapping = {
    "sample_location": location,
    "galaxy_api_key": key,
    "galaxy_server_address": address,
    "galaxy_port": port
  }

  # open config file...
  with open("{}/".format('/'.join(os.path.realpath(__file__).split('/')[:-1])) + config_file_name, 'r') as stream:
    try:
      config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print("Error parsing {}:\n\t{}".format(config_file_name, exc))

  # for each configurable argument (key)
  for k in config_to_args_mapping:
    # if the argument is not supplied, get it from config file:
    val = config_to_args_mapping[k]
    if not val:
      try:
        val = stream[k]
      except KeyError:
        print("KeyError: {} not found in {}".format( k, config_file_name))

  # check provided location exists
  if location:
    if not os.path.isdir(location):
      MIHCBase.err("'{}' is not a valid directory, setting `location` to current working directory".format(location))

  # otherwise set it to the calling directory
  else:
    location = getcwd()

  # check final parameter values
  for k in config_to_args_mapping:
    val = config_to_args_mapping[k]
    if k == "galaxy_port":
      if not val:
        config_to_args_mapping[k] = "80"
      elif isinstance(val, int):
        val = str(val)
    elif not val:
      raise Exception("Error: {} not defined".format(val))

  # arguments settled on, running MIHC scripts
  mihcrun = MIHCRunner(location, key, address, port)