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
        parser.add_option("--has_oov","",default=False,dest="has_oov",
                help="accept OOV words, default is false")
        (options,args) = parser.parse_args()

	if (len(args) != 1):
                parser.print_usage()
		sys.exit(-1)
	
	# accept OOV
	acceptOOV = (options.has_oov == 'True')

	# open phone list file
	( phonlist, ) = args


	try:
		plist_file = open(phonlist)
	except IOError:
		sys.stderr.write(sys.argv[0]+": Phone list file "+phonlist+" not found\n")
		sys.exit(-1)	

	
	plist = list()
	while True:
		line = plist_file.readline()
		if (line == ''):
			break
		line = line.rstrip('\n')		
		plist.append(line)
	plist_file.close()

	# parse mlf
	mlf_file = sys.stdin
	while True:
		line = mlf_file.readline()
		if (line == ''):
			break
		line = line.rstrip('\n')

		mlf_filename_pattern = re.compile(r'(\S+).rec"')
		mlf_content_pattern = re.compile(r'(\d+)\s+(\d+)\s+(\S+)\s+(\S+)')

		m1 = mlf_filename_pattern.search(line)
		m2 = mlf_content_pattern.search(line)
		
		if (m1):
			pass	# do nothing for the time being
		if (m2):
			seg_onset = m2.group(1)
			seg_offset = m2.group(2)
			seg_tx = m2.group(3)
			seg_llr = m2.group(4)					
			try:
				sys.stdout.write(str(plist.index(seg_tx)+1)+" ")
			except ValueError:
				if (acceptOOV):
					pass
				else:
					sys.stderr.write(sys.argv[0]+": Supplied mlf file contains units outside of the wordlist.\n")
					sys.exit(-1)
		elif (line == "."):
			sys.stdout.write("\n")




if __name__ == '__main__':
	main()
