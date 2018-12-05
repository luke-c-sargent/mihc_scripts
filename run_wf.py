#!/usr/bin/env python3

import argparse
import json

from datetime import datetime
from bioblend.galaxy import GalaxyInstance, libraries, histories

parser = argparse.ArgumentParser()
parser.add_argument('--addr')
parser.add_argument('--key')
parser.add_argument('--samples')
parser.add_argument('-v', action="store_true")
args = parser.parse_args()


#verbosity flag
_v = args.v

# bioblend objects
gi = GalaxyInstance(url=args.addr, key=args.key)
lib = libraries.LibraryClient(gi)
hist = histories.HistoryClient(gi)

LIBRARY_NAME = "mIHC Sample Data Repository"
SAMPLES = json.loads(args.samples)


# helpers
def dprint(strang):
  if _v:
    print(strang)

def get_lib(lib_name=LIBRARY_NAME):
  dprint("checking for library {}".format(lib_name))
  _r = lib.get_libraries(name=lib_name)
  if len(_r) > 1:
    raise Exception("there should be exactly one repo named {}.... {} found.".format(LIBRARY_NAME, len(_r)))
  elif len(_r) == 0:
    return None
  else:
    return _r[0]

def create_lib(lib_name=LIBRARY_NAME):
  dprint("creating library {}".format(lib_name))
  description = "the data library for mIHC sample data"
  return lib.create_library(lib_name, description)

def create_lib_folder(lib_id, folder_name):
  dprint("creating library folder {} in library id={}".format(lib_id, folder_name))
  lib.create_folder(lib_id, folder_name, description="Sample {}".format(folder_name))
  
def get_lib_folders(lib_id):
  dprint("checking for library id={} folders...".format(lib_id))
  return lib.get_folders(lib_id)

def upload_file_to_dir(lib_id, paths, folder_id):
    return lib.upload_from_galaxy_filesystem(lib_id, paths, folder_id, link_data_only="link_to_files")

# check for data library, create if not present
_l = get_lib()
if not _l:
  _l = create_lib()

dprint("lib info:\n{}".format(_l))

def process_sample(sample, lib_folders, lib_id):
  end_folder = list(sample.keys())[0].split('/')[-1]
  # is this folder present?
  _r = {}
  for _f in lib_folders:
    if _f["name"] == str("/" + end_folder):
      #raise Exception("folder '{}' already exists in data library '{}'".format(_f["name"], lib_id))
     _r = _f
     break
  # its not, create
  if not _r:
    _r = create_lib_folder(lib_id, end_folder)
  _folder_id = _r["id"]
  # add data
  _samples = sample[list(sample.keys())[0]]

  _nuclei = _samples["nuclei"]
  _images = _samples["images"]
  _image_string = ""
  for _i in _images:
    image_string = image_string + "{}\n".format(_id)
  _annot  = _samples["annoation"]
  _result_info = []
  for _in in (_nuclei, _annot, _image_string):
    _result_info.append(upload_file_to_dir(lib_id, _in, _folder_id))

  return _result_info


print(get_lib_folders(_l["id"]))

sample_info = []

for _s in SAMPLES:
  dprint("uploading sample {}".format(_s))
  lib_folders = get_lib_folders(_l["id"])
  sample_info.append(process_sample({_s:SAMPLES[_s]}, lib_folders, _l["id"]))

dprint(sample_info)
exit()

# create history
nonce = str(datetime.utcnow()).split('.')[0]
workflow_loc = "/home/lab/mybin/test_wf.ga"
wfname = workflow_loc.split('/')[-1]
history_info = hist.create_history(name="{} {}".format(wfmame, nonce))


# add datasets
hist.upload_dataset_from_library(history_id, lib_dataset_id)

# add dataset collection
e_ids = []

description = {
  "collection_type": "list",
  "element_identifiers": e_ids,
  "name": "Marker Image set"
}
hist.create_dataset_collection(history_id="", collection_description="")
# run workflow
