import argparse
import json

from datetime import datetime

from bioblend.galaxy import GalaxyInstance, workflows

from MIHCBase import MIHCBase
from MIHCGalaxyLibrary import MIHCGalaxyLibrary
from MIHCHistory import MIHCHistory

class MIHCGalaxy(MIHCBase):
  
  def __init__(self, galaxy_address, api_key, samples, lib_name=None):
    if not lib_name:
      lib_name = MIHCGalaxyLibrary.DEFAULT_LIBRARY_NAME
    self._gi = GalaxyInstance(url=galaxy_address, key=api_key)
    self._lib = MIHCGalaxyLibrary(self._gi, lib_name)
    self._wfc = workflows.WorkflowClient(self._gi)
    def add_workflow(d):
      if isinstance(d, dict):
        return self._wfc.import_workflow_dict(d)
      elif isfile(d):
        return self._wfc.import_workflow_from_local_path(d)
      else:
        self.err("No workflow found")
    self._hists = []
    _rs = []
    # samples = dict of MIHCData objects 
    # K: V == source directory: MIHCDataset Object
    for _s in samples: # each sample needs:
      _datatype_name = type(samples[_s]).__name__
      _r = {}
      # a history
      _hname = samples[_s].get_data()["source_dir"].split('/')[-1]
      _h = MIHCHistory(name=_hname, galaxy_instance=self._gi)
      # that history, populated
      _h.add_data(samples[_s], self._lib)
      _hinfo = _h.get_dataset_info()
      _ds_info = _hinfo["datasets"] #list with hda_ldda, id, dataset_id
      _dsc_info = _hinfo["dataset_collections"] #list with 
      
      _labels = samples[_s].get_inputs()
      #The map must be in the following format: {'<input_index>': {'id': <encoded dataset ID>, 'src': '[ldda, ld, hda, hdca]'}} (e.g. {'2': {'id': '29beef4fadeed09f', 'src': 'hda'}})

      # a workflow added
      _wf = samples[_s]._data["parent_workflow"]
      _r = add_workflow(_wf)
      _inputs = {}
      # for every label,
      for _l in _labels.keys():
        # get hdda / hda association
        _src = ""
        _data_src = None
        _data_id = None
        if _labels[_l] == list:
          _src = "hdca"
          _data_src = _dsc_info
        elif _labels[_l] == str:
          _src = "hda"
          _data_src = _ds_info
        for _d in _data_src:
          if _d["name"] == _l:
            _data_id = _d["id"]
            break
        _in_idx = self._wfc.get_workflow_inputs(_r["id"], _l)[0]
        _inputs[_in_idx] = {
          "id": _data_id,
          "src": _src
        }
      # a workflow invoked against that history
      self._wfc.invoke_workflow(_r["id"], inputs=_inputs, history_id=_h._data["id"])
      #collect results
