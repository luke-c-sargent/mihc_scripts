#!/usr/bin/env python3
import argparse
import json
from os import listdir,getcwd
from os.path import isfile, isdir

DEBUG = False 

parser = argparse.ArgumentParser()
parser.add_argument("location", nargs="?", default=getcwd())
parser.add_argument("-print", action="store_true")
args = parser.parse_args()

def dbg_log(string):
  if DEBUG:
    print(string)

# get location from first argument or, if absent, use dir script was called from
if args.location:
  if isdir(args.location):
    root = args.location
  else:
    print("provided location [{}] is not a directory".format(args.location))
    print("please provide a valid directory or no arguments to choose local directory")
    exit(1)
else:
  root = getcwd()

def is_mihc_folder(location, exclude_processed=True):
  _files, _dirs = list_dir(location)
  _result = {
    "images" : [],
    "nuclei" : "",
    "annotation" : "",
    "parent_workflow": ""
  }
  dbg_log("files in {}:\n\t{}".format(location, _files))
  # if we are excluding processed, do that
  if exclude_processed:
    if "Processed" in _dirs:
      return {}
  # is there an xml file?
  for f in _files:
    if f[-3:] == "xml":
      dbg_log("found xml file {}".format(f))
      _result["annotation"] = f
      # xml present, is complementary .svs also present?
      if str(f[:-3] + "svs") not in _files:
        print("ERROR: missing required nuclei image file: \n\t-[{}]".format(f[:-3] + "svs"))
        return {}
      else:
        dbg_log("adding nuclei file {}".format(f[:-3] + "svs"))
        _result["nuclei"] = f[:-3] + "svs"
    elif f[-3:] == "svs":
      _result["images"].append(f)
  if not _result["nuclei"] or not _result["annotation"]:
    dbg_log("no nuc:\n\t{}\nno annot:\n\t{}".format(_result["nuclei"], _result["annotation"]))
    return {}
  # remove nuclei file from images
  _result["images"].remove(_result["nuclei"])
  # find parent workflow
  _l = location if location[-1] != '/' else location[:-1]
  parent_dir = '/'.join(_l.split('/')[:-1])
  _files, _dirs = list_dir(parent_dir)
  _wf = ""
  for f in _files:
    if f[-3:] == ".ga":
      if not _wf:
        _wf = f
      else:
        raise Exception("Multiple workflows found where one was expected:\n\t{} and {}... quitting.".format(_wf, f))
  if _wf:
    _result["parent_workflow"] = _wf
  else:
    raise Exception("No workflows found in parent directory {}... quitting".format(parent_dir))
  return _result

def list_dir(location):
  dbg_log("listing location {}".format(location))
  _files = []
  _dirs  = []
  _contents = listdir(location)
  for c in _contents:
    c = location + "" if location[-1] == "/" else location + "/" + c
    if isfile(c):
      _files.append(c)
    elif isdir(c):
      _dirs.append(c)
    else:
      dbg_log("object '{}' is weird... skipping".format(c))
  return (_files, _dirs)

def find_mihc_data(location):
  possible_locations = [location]
  results = {}
  while possible_locations:
    dbg_log("possibles:\n{}".format(possible_locations))
    # pop the top entry
    _loc = possible_locations[0]
    dbg_log("checking {}...".format(_loc))
    possible_locations.remove(possible_locations[0])
    # check if out
    _mihc = is_mihc_folder(_loc)
    if _mihc:
      dbg_log("mihc: {}".format(_mihc))
      results[_loc] = _mihc
    else:
      possible_locations.extend(list_dir(_loc)[1])
      dbg_log(possible_locations)
  return results

def print_result(_r):
  print("{}: {} MIHC folders found".format(root, len(_r)))
  for folder in _r:
    _root = _r[folder]
    print(folder)
    print(" - wflow : {}".format(_root["parent_workflow"]))
    print(" - nuclei: {}".format(_root["nuclei"]))
    print(" - annot : {}".format(_root["annotation"]))
    print(" - images:")
    for i in _root["images"]:
      print("   - {}".format(i))

def create_ymls(datadict):
  for slide in datadict:
    # get path
    _path = slide
    # get inputs
    # 
    pass

_r = find_mihc_data(root)
if args.print:
  print(json.dumps(_r))
else:
  print_result(_r)


