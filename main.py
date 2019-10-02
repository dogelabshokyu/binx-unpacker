#Edit "binx_Extract.py"
#python 3.x

from struct import *
from optparse import OptionParser
import os


parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="input file to parse", default="")
parser.add_option("-o", "--outdir", action="store", type="string", dest="outdir", help="Output directory", default="./extract")
parser.add_option("-l", "--list", action="store_true", dest="list", help="List of partitions")
parser.add_option("-e", "--extract", action="store_true", dest="extract", help="Extract all partitions(without \"-n NAME\")", default = False)
parser.add_option("-n", "--name", action="store", type="string", dest="name", help="Extract partition by name", default = "")
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
        print("Build time : ",fw_build_time)
    f.seek(-4, 2)
    f.seek(unpack("I", f.read(4))[0])
    f.seek(16, 1)
    partitions = []
    json_partitions = {}
    while True:
        partition = dict(zip(('no1', 'no2', 'id', 'flash', 'start', 'zero', 'size1', 'size2', 'blocksize', 'pagesize', 'none', 'name'), unpack('2b h 7I 16s 16s', f.read(64))))
        f.seek(32, 1)
        partition['no'] = partition['no1']+partition['no2']
        if partition['no2'] != 4:
            partition['type'] = "MBR " + str(partition['no2'])
        if partition['no2'] == 4:
            partition['type'] = "EBR " + str(partition['no1'])
        if (partition['size1'] != partition['size2']):
            print("Invalid Partition %s" % partition['name'])
        if partition['flash'] == 340:
            partition['flash'] = "Yes"
        if partition['flash'] == 352:
            partition['flash'] = "No"
        partition['name'] = partition['name'].decode('ascii')
        partition['name'] = partition['name'].replace("\x00", "").replace("\x0A", "")
        #print(partition)
        partitions.append(partition)
        f.seek(4, 1)
        if f.read(4) == b'\x00\x00\x00\x00':
            print("\033[1;31mEnd Detected\033[0;0m")
            break
        else:
            f.seek(-8, 1)
    if options.list:
        print("No.  Name       MBR      Id    Flash  Start         Size           /bytes    Blocksize    Pagesize")
        for part in partitions:
            print("%-4i %-10s %-8s 0x%-3X %-6s 0x%08X    0x%08X (%9i)   0x%08X   0x%08X\n" % (part['no'], part['name'], part['type'], part['id'], part['flash'], part['start'], part['size1'], part['size1'], part['blocksize'], part['pagesize']))
    if (options.extract) | ((options.name) != ""):
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
        print("\033[1;31mThis is experimental function.\033[0;0m")
        print("output C:/pdl/test.txt")
        partiton_json = open("c:/pdl/test.txt", 'w')
        for data in partitions:
            print(data)
            partiton_json.write(str(data)+"\n")
    if options.debug:
        print("Not yet")
    f.close()