#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import sys
import os
import re
from optparse import OptionParser

##########################
# MAIN
##########################
def main():

	# Parse options
	parser = OptionParser()
	parser.usage = "%prog [options] <word_list>"
	parser.add_option("--oov",action="store_true",default=False,dest="acceptOOV",
		help="accept OOV words, default is false")
	(options,args) = parser.parse_args()

	if (len(args) != 1):
		parser.print_usage()
		sys.exit(-1)
	( wordlist, ) = args

	# open word list file
	try:
		plist_file = open(wordlist)
	except IOError:
		sys.stderr.write(sys.argv[0]+": Phone list file "+wordlist+" not found\n")
		sys.exit(-1)	

	
	plist = list()
	while True:
		line = plist_file.readline()
		if (line == ''):
			break
		line = line.rstrip('\n')		
		plist.append(line)
	plist_file.close()

	# parse stm
	stm_file = sys.stdin
	while True:
		line = stm_file.readline()
		if (line == ''):
			break
		line = line.rstrip('\n')

		stm_content_pattern = re.compile(r'(\S+)\s+(\d+)\s+(\S+)\s+(\d+.\d+)\s+(\d+.\d+)\s+(\S+)\s+(.*)')

		m = stm_content_pattern.search(line)

		if (m):
			seg_filename = m.group(1)
			seg_channel = m.group(2)
			seg_speaker = m.group(3)
			seg_onset = m.group(4)
			seg_offset = m.group(5)
			seg_tag = m.group(6)
			seg_tx = m.group(7).lstrip().rstrip().split()
			
			
			try:
				prev_seg_filename
				if (seg_filename != prev_seg_filename):
					addNewLine = 1
				else:
					addNewLine = 0
			except NameError:
				addNewLine = 0

			
			if (addNewLine):
				sys.stdout.write("\n")

			for i in range(0,len(seg_tx)):
				try:
					sys.stdout.write(str(plist.index(seg_tx[i])+1)+" ")
				except ValueError:
					if (options.acceptOOV):
						pass
					else:
						sys.stderr.write(sys.argv[0]+": Supplied stm file contains units outside of the wordlist.\n")
						sys.exit(-1)
			prev_seg_filename = seg_filename
	# WRite new line at the very end
	sys.stdout.write("\n")


if __name__ == '__main__':
	main()
