import argparse
import json

from datetime import datetime
from os.path import isfile

from bioblend.galaxy import GalaxyInstance, workflows

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
    self._gi = GalaxyInstance(url=galaxy_address, key=api_key)
    self._wfc = workflows.WorkflowClient(self._gi)
    # initialize Galaxy Library object
    self._lib = MIHCGalaxyLibrary(self._gi, lib_name)

    # sub-method to add workflow(s) to Galaxy instance via path to file or dict
    def add_workflow(d):
      # get existing workflows
      existing_wfs = self._wfc.get_workflows()
      # sub-sub-method to extract workflow via ID
      def get_workflow_from_id(id):
        for wf in existing_wfs:
          if wf["latest_workflow_uuid"] == id:
            return wf
        return {}

      given_wf_uuid = ""
      if isinstance(d, dict):
        given_wf_uuid = dict["uuid"]
        extant_wf = get_workflow_from_id(given_wf_uuid)
        if extant_wf:
          return extant_wf
        # FIXME: DETERMINE IF YOU SHOULD THEN DO OTHER THINGS
        return self._wfc.import_workflow_dict(d)
      elif isfile(d):
        _info = ""
        with open(d) as f:
          _info = f.read().replace(': null', ': None')
        given_wf_uuid = json.loads(_info)["uuid"]
        extant_wf = get_workflow_from_id(given_wf_uuid)
        if extant_wf:
          return extant_wf
        return self._wfc.import_workflow_from_local_path(d)
      else:
        self.err("No workflow found")

    # initialize history list and results
    self._hists = []
    _rs = []
    # samples = dict of MIHCData objects 
    # K: V == source directory: MIHCDataset Object

    invoked_workflows = []
    # main sample-processing loop
    for _s in samples: # each sample needs:
      # library sync
      samples[_s].library_sync(self._lib)
      _datatype_name = type(samples[_s]).__name__
      _r = {}
      # a history to populate
      _hname = samples[_s].get_data()["source_dir"].split('/')[-1]
      _h = MIHCHistory(name=_hname, galaxy_instance=self._gi)
      # that history, populated
      _h.add_data(samples[_s], self._lib)
      _hinfo = _h.get_dataset_info()
      _ds_info = _hinfo["datasets"] #list with hda_ldda, id, dataset_id
      _dsc_info = _hinfo["dataset_collections"] #list with 
      
      _labels = samples[_s].get_inputs()
      #The map must be in the following format: 
      #  {'<input_index>': 
      #      {'id': <encoded dataset ID>, 'src': '[ldda, ld, hda, hdca]'}} 
      # (e.g. {'2': {'id': '29beef4fadeed09f', 'src': 'hda'}})

      # a workflow added
      _sample_data = samples[_s]._data
      _wf = _sample_data["parent_workflow"]
      _r = add_workflow(_wf)
      _inputs = {}
      # for every label,
      for _l in _labels.keys():
        _label_file_path = _sample_data[_l]
        # get hdda / hda association
        _src = ""
        _data_src = None
        _data_id = None
        _data_type = None
        # determine if its a dataset or dataset_collection
        if _labels[_l] == list:
          _src = "hdca"
          _data_src = _dsc_info
          _data_type = "dataset_collection"
        elif _labels[_l] == str:
          _src = "hda"
          _data_src = _ds_info
          _data_type = "dataset"
        for _d in _data_src:
          if _d["history_content_type"] == 'dataset_collection':
            if _d["name"] == _l:
              _data_id = _d["id"]
              break
          elif _d["history_content_type"] == 'dataset':
            if _d["file_name"] == _sample_data[_l]:
              _data_id = _d["id"]
              break
        _in_idx = self._wfc.get_workflow_inputs(_r["id"], _l)[0]
        _inputs[_in_idx] = {
          "id": _data_id,
          "src": _src
        }

      # invoke workflow and collect results
      print("Invoking workflow: \n\t{}\nOn History {}".format(_wf, _hname))
      wf_return = self._wfc.invoke_workflow(_r["id"], inputs=_inputs, history_id=_h._data["id"])
      # get the start time
      wf_return["start_datetime"] = datetime.utcnow()
      invoked_workflows.append(wf_return)

    # Now, check each of those invoked workflows for progress
    #   1. get workflow invocation /api/workflows/{id}/invocations/{id}?key={key}&step_details=true
    #   2. check invocation["steps"]
    #        - for each step,
    #            - if jobs and jobs_id,
    #              - for each job in jobs,
    #                - if state != "ok" || exit_code != 0
    #                   goto 1 after timeout
    #   3. if no error in 2, it's finished!
