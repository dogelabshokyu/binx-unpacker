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
    f.seek(unpack("I", f.read(4))[0])
    f.seek(16, 1)
    partitions = []
    while True:
        if f.read(4) == "\x00\x00\x00\x00":
            break
        f.seek(-4, 1)
        loop = loop + 1
        print(loop,"partition count")
        print(unpack('2b h 7I 16s 48s', f.read(96)))
    print('end')