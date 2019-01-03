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
      print(_s)
      _r = {}
      # a history
      _hname = samples[_s].get_data()["source_dir"].split('/')[-1]
      _h = MIHCHistory(name=_hname, galaxy_instance=self._gi)
      # that history, populated
      _h.add_data(samples[_s], self._lib)
      _hinfo = _h.get_dataset_info()
      _ds_info = _hinfo["datasets"] #list with hda_ldda, id, dataset_id
      _dsc_info = _hinfo["dataset_collections"] #list with 
      
      #The map must be in the following format: {'<input_index>': {'id': <encoded dataset ID>, 'src': '[ldda, ld, hda, hdca]'}} (e.g. {'2': {'id': '29beef4fadeed09f', 'src': 'hda'}})
      
      print("DS:\n{}\nDSC:\n{}\n!!!!!!!!!!!!!!!!!!!!!!!".format(_ds_info, _dsc_info))
      exit()
      # a workflow added
      _wf = samples[_s]._data["parent_workflow"]
      _r = add_workflow(_wf)
      # a workflow invoked against that history
      self._wfc.invoke_workflow(_r["id"], inputs=_inputs, history_id=_h._data["id"])
      #collect results
