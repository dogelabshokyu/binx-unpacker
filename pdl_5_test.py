#!/usr/bin/python3

from struct import *
from optparse import OptionParser
from pyprnt import prnt
import os
import json

parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="input file to parse",
                  default="")

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
# read section info offset
f.seek(-8, 2)
f.seek(unpack("Q", f.read(0x08))[0], 0)

# start sectioninfo header (length = Hdr_size_)
sect_info_hdr_Ver = unpack("I", f.read(0x04))[0]
sect_info_hdr_Hdr_size_ = unpack("I", f.read(0x04))[0]
sect_info_hdr_Pdl_checksum_ = f.read(0x04).hex()
sect_info_hdr_Cnt_ = unpack("I", f.read(0x04))[0]  # int.from_bytes(f.read(0x04), byteorder='little')
sect_info_hdr_Struct_size_ = unpack("I", f.read(0x04))[0]  # int.from_bytes(f.read(0x04), byteorder='little')
f.seek(0x08, 1)
f.seek(0x08, 1)

#####################################
PDL_INFO = {"PDL Version": sect_info_hdr_Ver, "Model": MODEL_NAME, "FW Version": PANTECH_BUILD_VER,
            "FW Build Date": fw_build_date, "FW Build time": fw_build_time}
PDL_section_info = {"Section Head Length": sect_info_hdr_Hdr_size_, "All section checksum": sect_info_hdr_Pdl_checksum_,
                    "Section Index": sect_info_hdr_Cnt_, "Section struct size": sect_info_hdr_Struct_size_}
PDL = [PDL_INFO, PDL_section_info]
prnt(PDL)
partitions = []
for i in range(sect_info_hdr_Cnt_):
    Section = {}
    Section_No_ = unpack("I", f.read(0x04))[0]
    Section_Type_ = unpack("I", f.read(0x04))[0]
    Section_Start = unpack("I", f.read(0x04))[0]
    f.seek(0x08, 1)
    Section_sz_0 = unpack("I", f.read(0x04))[0]
    f.seek(0x04, 1)
    Section_sz_1 = unpack("I", f.read(0x04))[0]
    f.seek(0x04, 1)
    Section_Block_sz = unpack("I", f.read(0x04))[0]
    Section_Page_sz = unpack("I", f.read(0x04))[0]
    f.seek(0x14, 1)
    Section_Name = f.read(0x0C).decode()
    f.seek(0x10, 1)
    Section_Checksum = f.read(4).hex().upper()
    if Section_sz_0 == Section_sz_1:
        Section_sz = Section_sz_0
    else:
        print("No : ", Section_No_, "File Size Different")
    Section = {"No": Section_No_, "Type": Section_Type_, "Size": Section_sz, "BlockSize": Section_Block_sz,
               "PageSize": Section_Page_sz, "Name": Section_Name, "Checksum": Section_Checksum}
    partitions.append(Section)
prnt(partitions)
