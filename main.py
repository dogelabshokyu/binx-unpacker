#!/usr/bin/python3

from struct import *
from optparse import OptionParser
import os
import json

parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="input file to parse", default="")
parser.add_option("-o", "--outdir", action="store", type="string", dest="outdir", help="Output directory", default="./extract")
parser.add_option("-l", "--list", action="store_true", dest="list", help="List of partitions")
parser.add_option("-e", "--extract", action="store_true", dest="extract", help="Extract all partitions(without \"-n NAME\")", default = False)
parser.add_option("-n", "--name", action="store", type="string", dest="name", help="Extract partition by name", default="")
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Turn on Debug Mode")
parser.add_option("-p", "--partition", action="store_true", dest="partition", help="Extract partition info as JSON file")

(options, args) = parser.parse_args()
if options.filename == "":
    if str(args) == "[]":
        print("Use -h to get help")
    else:
        options.filename = args[0]
if options.filename != "":
    f = open(options.filename, "rb")
    if f.read(16).decode() == "$PDL_PHONE_INFO_":
        print("\x1b[6;30;42mPHONE INFO Detected\x1b[0m")
        f.seek(36, 0)
        phone_model = f.read(16).decode().replace("\x00", "")
        print("Model : ", phone_model)
        f.seek(52, 0)
        fw_version = f.read(16).decode().replace("\x00", "")
        print("Version : ", fw_version)
        f.seek(76, 0)
        fw_build_time = f.read(32).decode().replace("\x00", "")
        print("Build time : ", fw_build_time)
    f.seek(-20, 2)
    sectioninfo_checksum = f.read(4).hex()
    f.seek(12, 1)
    f.seek(unpack("I", f.read(4))[0])
    pdl_ver = f.read(4).hex()
    pdl_image_checksum = f.read(4).hex()
    print("PDL Ver : ", pdl_ver)
    print("PDL Checksum : ", pdl_image_checksum)
    print("SectionInfo Checksum : ", sectioninfo_checksum.upper())
    f.seek(8, 1)
    partitions = []
    while True:
        partition = dict(zip(('no1', 'no2', 'id', 'flash', 'start', 'zero', 'size1', 'size2', 'blocksize', 'pagesize', 'none', 'name'), unpack('2b h 7I 16s 16s', f.read(64))))
        f.seek(12, 1)
        partition['checksum'] = f.read(4).hex().upper()
        #print(partition['checksum'])
        f.seek(16, 1)
        #f.seek(32, 1)
        partition['no'] = partition['no1']+partition['no2']
        if partition['no2'] != 4:
            partition['type'] = "MBR " + str(partition['no2'])
        if partition['no2'] == 4:
            partition['type'] = "EBR " + str(partition['no1'])
        if partition['size1'] != partition['size2']:
            print("Invalid Partition %s" % partition['name'])
        if partition['flash'] == 340:
            partition['flash'] = "Yes"
        if partition['flash'] == 352:
            partition['flash'] = "No"
        partition['name'] = partition['name'].decode('ascii')
        partition['name'] = partition['name'].replace("\x00", "").replace("\x0A", "").replace("\x01", "")
        partitions.append(partition)
        f.seek(4, 1)
        if f.read(4) == b'\x00\x00\x00\x00':
            print("\033[94mRead Partition Info Sucess\n\033[1;31mEnd Detected\033[0;0m")
            break
        else:
            f.seek(-8, 1)
    if options.list:
        print("No.  Name       MBR      Id    Flash  Start         Size            /bytes    Blocksize    Pagesize     Checksum")
        for part in partitions:
            print("%-4i %-10s %-8s 0x%-3X %-6s 0x%08X    0x%08X (%10i)   0x%08X   0x%08X   %08s\n" % (part['no'], part['name'], part['type'], part['id'], part['flash'], part['start'], part['size1'], part['size1'], part['blocksize'], part['pagesize'], part['checksum']))
    if options.extract | ((options.name) != ""):
        for part in partitions:
            if (options.name) != "":
                if (part['name'].lower() != options.name.lower()):
                    continue
            if not os.path.exists(options.outdir + "/" + phone_model + "_" + fw_version):
                os.makedirs(options.outdir + "/" + phone_model + "_" + fw_version)
            o = open(options.outdir + "/" + phone_model + "_" + fw_version + "/" + str(part['no']) + "_" + part['name'] + ".img", "wb")
            f.seek(part['start'])
            if (part['blocksize'] == part['size1']):
                o.write(f.read(part['size1']))
            else:
                for x in range(part['size1']):
                    o.write(f.read(part['blocksize']))
                    if (o.tell() == part['size1']): break
            o.close()
            print("Extract %i_%s.img" % (part['no'], part['name']))
    if options.partition:
        print("extracting partition info as JSON")
        total_section = len(partitions)
        print("total sector :", total_section)
        json_partitions = {"PDL_Partitions": {}}
        json_partitions["PDL_Partitions"] = {"Model": phone_model, "Version": fw_version, "Build_time": fw_build_time, "Partition_info": {}}
        for i in range(total_section):
            sector_name = "section" + str(i)
            sector_dict = {sector_name: {"no1": partitions[i]['no1'],
                                         "no2": partitions[i]['no2'],
                                         "id": partitions[i]['id'],
                                         "flash": partitions[i]['flash'],
                                         "start": partitions[i]['start'],
                                         "zero": partitions[i]['zero'],
                                         "size1": partitions[i]['size1'],
                                         "size2": partitions[i]['size2'],
                                         "blocksize": partitions[i]['blocksize'],
                                         "pagesize": partitions[i]['pagesize'],
                                         "name": partitions[i]['name']
                                         }
                           }
            json_partitions["PDL_Partitions"]["Partition_info"].update(sector_dict)
        partitions_dump = json.dumps(json_partitions, ensure_ascii=False)
        json_file = open("./"+"PDL_Partition_info_"+phone_model+"_"+fw_version+".json", "w")
        json_file.write(partitions_dump)
        json_file.close()
    if options.debug:
        print("Not yet")
    f.close()