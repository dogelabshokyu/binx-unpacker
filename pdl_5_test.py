#!/usr/bin/python3

from struct import *
from optparse import OptionParser
from pyprnt import prnt
import os
import json

parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="input file to parse", default="")

(options, args) = parser.parse_args()

f = open(options.filename, "rb")
if f.read(0x16).decode() == "$PDL_PHONE_INFO_MAGIC$":
    # check fw info
    print("\x1b[6;30;42mPHONE INFO Detected\x1b[0m")
    f.seek(0x0E, 1)
    phone_model = f.read(0x10).decode().replace("\x00", "")
    fw_version = f.read(0x10).decode().replace("\x00", "")
    f.seek(0x08, 1)
    fw_build_date = f.read(0x10).decode().replace("\x00", "")
    fw_build_time = f.read(0x10).decode().replace("\x00", "")
#read section info offset
f.seek(-8, 2)
f.seek(unpack("I", f.read(0x04))[0], 0)
# start section head (length : 36bytes)
pdl_ver = f.read(0x04).hex()

PDL_INFO = {"PDL Version" : pdl_ver, "Model" : phone_model, "FW Version" : fw_version, "FW Build Date" : fw_build_date,
            "FW Build time" : fw_build_time}