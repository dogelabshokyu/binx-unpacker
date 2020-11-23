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
    MODEL_NAME = f.read(0x10).decode().replace("\x00", "")
    PANTECH_BUILD_VER = f.read(0x10).decode().replace("\x00", "")
    f.seek(0x08, 1)
    fw_build_date = f.read(0x10).decode().replace("\x00", "")
    fw_build_time = f.read(0x10).decode().replace("\x00", "")
print("\n\x1b[6;30;42mReading Section info\x1b[0m")
#read section info offset
f.seek(-8, 2)
f.seek(unpack("I", f.read(0x04))[0], 0)
# start section head (length = pdl_section_head_length)
pdl_ver = unpack("I", f.read(0x04))[0]
pdl_section_head_length = unpack("I", f.read(0x04))[0]
pdl_checksum = f.read(0x04).hex()
pdl_section_index = unpack("I", f.read(0x04))[0] #int.from_bytes(f.read(0x04), byteorder='little')
pdl_section_struct_size = unpack("I", f.read(0x04))[0] #int.from_bytes(f.read(0x04), byteorder='little')
f.seek(0x08, 1)
f.seek(0x08, 1)


#####################################
PDL_INFO = {"PDL Version" : pdl_ver, "Model" : MODEL_NAME, "FW Version" : PANTECH_BUILD_VER, "FW Build Date" : fw_build_date,
            "FW Build time" : fw_build_time}
PDL_section_info = {"Section Head Length" : pdl_section_head_length, "All section checksum" : pdl_checksum,
                    "Section Index" : pdl_section_index, "Section struct size" : pdl_section_struct_size}
PDL = [PDL_INFO, PDL_section_info]
prnt(PDL)
'''
for i in range(pdl_section_index):
    section =
'''