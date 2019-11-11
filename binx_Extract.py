#-*-coding:utf-8-*-
#!/usr/bin/python
# archive original code
from struct import *
from optparse import OptionParser
import os

parser = OptionParser()
parser.add_option("-i", "--input", action="store", type="string", dest="filename", help="Input file to parse", default = "")
parser.add_option("-o", "--outdir", action="store", type="string", dest="outdir", help="Output directory", default="./extract")
parser.add_option("-l", "--list", action="store_true", dest="list", help="List of partitions")
parser.add_option("-e", "--extract", action="store_true", dest="extract", help="Extract all partitions(without \"-n NAME\")", default = False)
parser.add_option("-n", "--name", action="store", type="string", dest="name", help="Extract partition by name", default = "")
(options, args) = parser.parse_args()
if options.filename == "":
	if str(args) == "[]":
		print("请使用“Extract.py -h”查看帮助")
	else:
		options.filename = args[0]
if options.filename != "":
	f = open(options.filename, "rb")
	f.seek(-4, 2)
	f.seek(unpack("I", f.read(4))[0])
	f.seek(16,1)
	partitions = [ ]
	while True:
		if f.read(4) == "\x00\x00\x00\x00":
			break
		f.seek(-4, 1)
		partition = dict(zip(('no1', 'no2', 'id', 'flash', 'start', 'zero', 'size1', 'size2', 'blocksize', 'pagesize', 'none', 'name'), unpack('2b h 7I 16s 48s', f.read(96))))
		partition['name'] = partition['name'].replace("\x00", "").replace("\x0A", "")
		partition['no'] = partition['no1']+partition['no2']
		if partition['no2'] != 4:
			partition['type'] = "MBR "+str(partition['no2'])
		if partition['no2'] == 4:
			partition['type'] = "EBR "+str(partition['no1'])
		if (partition['size1'] != partition['size2']):
			print("分区'%s'的大小信息不明" % partition['name'])
		if partition['flash'] == 340:
			partition['flash'] = "Yes"
		if partition['flash'] == 352:
			partition['flash'] = "No"
		partitions.append(partition)
	if (options.list):
		print("No.  Name       MBR      Id    Flash  Start         Size           /bytes    Blocksize    Pagesize")
		for part in partitions:
			print("%-4i %-10s %-8s 0x%-3X %-6s 0x%08X    0x%08X (%9i)   0x%08X   0x%08X\n" % (part['no'], part['name'], part['type'], part['id'], part['flash'], part['start'], part['size1'], part['size1'], part['blocksize'], part['pagesize']))
	if (options.extract) | ((options.name) != ""):
		for part in partitions:
			if (options.name) != "":
				if (part['name'].lower() != options.name.lower()):
					continue
			if not os.path.exists(options.outdir):
				os.makedirs(options.outdir)
			o = open(options.outdir+"/"+str(part['no'])+"_"+part['name']+".img", "wb")
			f.seek(part['start'])
			if (part['blocksize'] == part['size1']):
				o.write(f.read(part['size1']))
			else:
				for x in xrange(part['size1']):
					o.write(f.read(part['blocksize']))
					if (o.tell() == part['size1']): break
			o.close()
			print("%i_%s.img已导出" % (part['no'], part['name']))
	f.close()
