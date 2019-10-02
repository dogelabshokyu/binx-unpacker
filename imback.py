#Edit "binx_Extract.py"
#python 3.x

from struct import *
from optparse import OptionParser

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
    f.seek(-8, 2)
    f.seek(unpack("I", f.read(4))[0])
    f.seek(16, 1)
    partitions = []
    json_partitions = {}
    while True:
        print(f.read(96))
        f.seek(-96, 1)
        partition = dict(zip(('no1', 'no2', 'id', 'flash', 'start', 'zero', 'size1', 'size2', 'blocksize', 'pagesize', 'none', 'name'), unpack('2b h 7I 16s 48s', f.read(96))))
        #print(partition)
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