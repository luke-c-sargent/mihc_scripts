#!/usr/bin/env python3
from MIHCRunner import MIHCRunner
import argparse
from sys import path

directory = path[0]

parser = argparse.Argument_Parser()
parser.add_argument("-k", "--api_key", type=str, help="executing user's API key")
parser.add_argument("-p", "--port", type=str, help="port the local galaxy is listening on")
parser.add_argument("-l", "--api_key", type=str, help="location to scan")

args = parser.parse_args()

if args.l:
  direcory = args.l

mihcrun = MIHCRunner(directory, args.k, "localhost", args.p)
