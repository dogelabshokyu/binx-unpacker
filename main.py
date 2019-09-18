#Edit "binx_Extract.py"
#python 3.x

from struct import *
from optparse import OptionParser
import binascii
loop = 0


parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="input file to parse", default="")
parser.add_option("-o", "--outdir", action="store", type="string", dest="outdir", help="Output directory", default="./extract")
parser.add_option("-l", "--list", action="store_true", dest="list", help="List of partitions")
parser.add_option("-e", "--extract", action="store_true", dest="extract", help="Extract all partitions(without \"-n NAME\")", default = False)
parser.add_option("-n", "--name", action="store", type="string", dest="name", help="Extract partition by name", default = "")
(options, args) = parser.parse_args()
if options.filename == "":
    if str(args) == "[]":
        print("Use -h to get help")
    else:
        options.filename = args[0]
if options.filename != "":
    f = open(options.filename, "rb")
    f.seek(-4, 2)
    print(unpack("I", f.read(4))[0])
    f.seek(-4, 2)
    f.seek(unpack("I", f.read(4))[0])
    f.seek(16, 1)
    partitions = []
    while True:
        if f.read(4) == "\x0A\x0A\x0A":
            print("\033[1;31mZero Detected\n\033[0;0m")
            break

        if loop < 12:
            f.seek(-4, 1)
            loop = loop + 1
            print("\033[1;36m", loop, "partition count\033[0;0m")
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
            print("\033[1;36m",partition,"\033[0;0m")
            #print("\033[0;32m",partition,"\033[0;0m")
            #print("\033[1;95m",partition['name'].decode(),"\033[0;0m")
            partitions.append(partition)
        else:
            print("\033[1;31mbreak while\n\033[0;0m")
            break
    print("No.  Name       MBR      Id    Flash  Start         Size           /bytes    Blocksize    Pagesize")
    for part in partitions:
        print("%-4i %-10s %-8s 0x%-3X %-6s 0x%08X    0x%08X (%9i)   0x%08X   0x%08X\n" % (part['no'], part['name'], part['type'], part['id'], part['flash'], part['start'], part['size1'], part['size1'], part['blocksize'], part['pagesize']))

'''
            print("\033[1;36m",loop,"partition count\033[0;0m")
            partition_data = unpack('2b h 7I 16s 48s', f.read(96))
            print(partition_data)
        else:
            print(f.read(4).decode('utf-16'))
            print("\033[1;31mbreak while\n\033[0;0m")
    print("line 36")
    print(f.read(4).decode('utf-16'))
    if (options.list):
        print("coding partition listing")
    if (options.extract):
        print("coding extracting")
    if (options.outdir) != './extract':
        print(options.outdir)
'''
