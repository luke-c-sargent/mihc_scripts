#!/usr/bin/env python3

from Detector import Detector
from MIHCDataset import MIHCDataset

test_input = {}

for _x in MIHCDataset.KEY_WHITELIST:
  test_input[_x] = "/tmp/test" if _x != "images" else ["/tmp/test", "/tmp/test"]

a = MIHCDataset("/some/dir", **test_input)

print(a.get_data())
