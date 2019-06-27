import argparse
import json
import time
import tarfile

from datetime import datetime
from os.path import isfile, isdir
from os import mkdir, remove

from bioblend.galaxy import GalaxyInstance, workflows, datasets

from mihc_scripts.MIHCBase.mihcbase import MIHCBase
from mihc_scripts.MIHCGalaxyLibrary.mihclibrary import MIHCGalaxyLibrary
from mihc_scripts.MIHCHistory.mihchistory import MIHCHistory

class MIHCGalaxy(MIHCBase):
  """Initializes and contains other Galaxy-related classes"""
  def __init__(self, galaxy_address, api_key, samples, lib_name=None):
    # determine / set name of library
    if not lib_name:
      lib_name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    # initialize bioblend objects
    self._galaxy_instance = GalaxyInstance(url=galaxy_address, key=api_key)
    self._workflow_client = workflows.WorkflowClient(self._galaxy_instance)
    self._dataset_client = datasets.DatasetClient(self._galaxy_instance)
    # configure dataset_client
    self._dataset_client.set_max_get_retries(4)
    # initialize Galaxy Library object
    self._lib = MIHCGalaxyLibrary(self._galaxy_instance, lib_name)
    invoked_workflows = self.process_samples(samples)
    self.monitor_workflows(invoked_workflows)

  def download_dataset(self, dataset_id, file_path, name, subdir="Processed"):
    # ensure directory exists or create it
    final_path = file_path + "/" + subdir
    tempdir = "/tmp/mihc_temp/"
    tempfile = "{}{}".format(tempdir, name)
    print("Path to place downloaded file: {}".format(final_path))
    if not isdir(final_path):
      mkdir(final_path)
    if not isdir(tempdir):
      mkdir(final_path)
    # call API
    #self._dataset_client.download_dataset(dataset_id, final_path, use_default_filename=False)
    self._dataset_client.download_dataset(dataset_id, tempfile, use_default_filename=False)
    # untar temp
    tar_file = tarfile.open(tempfile, "r:gz")
    tar_file.extractall(path=final_path)
    # delete temp
    remove(tempfile)

  def process_samples(self, samples):
    """Takes collected samples & workflows, adds them to a history & executes
    returns invoked_workflows, list of dicts representing execution with keys:
      - "start_datetime" : datetime of execution
      - "directory" = where the samples live (and where to put output)
      - "history_object" = associated bioblend history object
    """
    # sub-method to add workflow(s) to Galaxy instance via path to file or dict
    def add_workflow(d):
      # get existing workflows
      existing_workflows = self._workflow_client.get_workflows()
      # sub-sub-method to extract workflow via ID
      def get_workflow_from_id(id):
        for _workflow in existing_workflows:
          if _workflow["latest_workflow_uuid"] == id:
            return _workflow
        return {}

      given_workflow_uuid = ""
      if isinstance(d, dict):
        given_workflow_uuid = dict["uuid"]
        extant_wf = get_workflow_from_id(given_workflow_uuid)
        if extant_wf:
          return extant_wf
        # FIXME: DETERMINE IF YOU SHOULD THEN DO OTHER THINGS
        return self._workflow_client.import_workflow_dict(d)
      elif isfile(d):
        _info = ""
        with open(d) as f:
          _info = f.read()
        given_workflow_uuid = json.loads(_info)["uuid"]
        extant_wf = get_workflow_from_id(given_workflow_uuid)
        if extant_wf:
          return extant_wf
        return self._workflow_client.import_workflow_from_local_path(d)
      else:
        self.err("No workflow found")
    # K: V == source directory: MIHCDataset Object

    invoked_workflows = []
    # main sample-processing loop
    for _sample_dir in samples: # each sample needs:
      # library sync
      samples[_sample_dir].library_sync(self._lib)
      _datatype_name = type(samples[_sample_dir]).__name__
      _results = {}
      # a history to populate
      _history_name = samples[_sample_dir].get_data()["source_dir"].split('/')[-1]
      _history_obj = MIHCHistory(name=_history_name, galaxy_instance=self._galaxy_instance)
      # that history, populated
      _history_obj.add_data(samples[_sample_dir], self._lib)
      _history_info = _history_obj.get_dataset_info()
      _dataset_info = _history_info["datasets"] #list with hda_ldda, id, dataset_id
      _dataset_collection_info = _history_info["dataset_collections"]

      _labels = samples[_sample_dir].get_inputs()
      #The map must be in the following format:
      #  {'<input_index>':
      #      {'id': <encoded dataset ID>, 'src': '[ldda, ld, hda, hdca]'}}
      # (e.g. {'2': {'id': '29beef4fadeed09f', 'src': 'hda'}})

      # a workflow added
      _sample_data = samples[_sample_dir]._data
      _workflow = _sample_data["parent_workflow"]
      _results = add_workflow(_workflow)
      _inputs = {}
      # for every label,
      for _label in _labels.keys():
        _label_file_path = _sample_data[_label]
        # get hdda / hda association
        _src = ""
        _data_src = None
        _data_id = None
        _data_type = None
        # determine if its a dataset or dataset_collection
        if _labels[_label] == list:
          _src = "hdca"
          _data_src = _dataset_collection_info
          _data_type = "dataset_collection"
        elif _labels[_label] == str:
          _src = "hda"
          _data_src = _dataset_info
          _data_type = "dataset"
        for _d in _data_src:
          if _d["history_content_type"] == 'dataset_collection':
            if _d["name"] == _label:
              _data_id = _d["id"]
              break
          elif _d["history_content_type"] == 'dataset':
            if _d["file_name"] == _sample_data[_label]:
              _data_id = _d["id"]
              break
        _in_idx = self._workflow_client.get_workflow_inputs(_results["id"], _label)[0]
        _inputs[_in_idx] = {
          "id": _data_id,
          "src": _src
        }

      # invoke workflow and collect results
      print("Invoking workflow: \n\t{}\nOn History {}".format(_workflow, _history_name))
      wf_return = self._workflow_client.invoke_workflow(_results["id"], inputs=_inputs, history_id=_history_obj._data["id"])
      # get the start time
      wf_return["start_datetime"] = datetime.utcnow()
      wf_return["directory"] = _sample_dir
      wf_return["history_object"] = _history_obj
      invoked_workflows.append(wf_return)
    return invoked_workflows

  def monitor_workflows(self, invoked_workflows):
    potential_downloads = {}
    for invoked_wf in invoked_workflows:
      potential_downloads[invoked_wf["history_id"]] = {}
    stop_processing = False
    while(not stop_processing):
      stop_processing = True
      # for every invoked workflow,
      for invoked_wf in invoked_workflows:
        _history_id = invoked_wf["history_id"]
        print("\nChecking invoked workflow id {} in history {} on data:\n\t-- {}".format(invoked_wf["workflow_id"], invoked_wf["history_id"], invoked_wf["directory"]))
        contents = invoked_wf["history_object"].get_history_contents()
        desired_contents = {}
        for _content in contents:
          if "extension" in _content and _content["extension"] == "zip" and "ROI" in _content["name"]:
            print("\t~found {}".format(_content["name"]))
            desired_contents[_content["name"]] = {"dataset_id": _content["id"], "file_path": invoked_wf["directory"]}
        # if we've already established this set,
        if not desired_contents or desired_contents != potential_downloads[_history_id]:
          potential_downloads[_history_id].update(desired_contents)
          stop_processing = False
        #print("status is:\n{}".format(invoked_wf["history_object"].get_history_contents()))
      time.sleep(20)
      #if stop_processing:
        #print("dc: {}\npd[hid]: {}".format(desired_contents, potential_downloads[_history_id]))

    # for each history item...
    for _hid in potential_downloads:
      _pd_item  = potential_downloads[_hid]
      # for each ROI...
      for _name in _pd_item:
        item = _pd_item[_name]
        print("Downloading dataset {} into {}".format(item["dataset_id"], item["file_path"], _name))
        self.download_dataset( item["dataset_id"], item["file_path"])
