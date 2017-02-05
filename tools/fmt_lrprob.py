#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import sys
import re
import numpy as np
from StringIO import StringIO
from optparse import OptionParser


def get_lrfamily_idx(trainlx,lx_family):

	# assume universal strlen to lx_familiy
	lx_family_strlen = len(lx_family[0])

	lx_family_mapping = [[] for i in range(0,len(lx_family))]

	for i in range(0,len(lx_family)):
		for j in range(0,len(trainlx)):
			if trainlx[j][0:lx_family_strlen] == lx_family[i]:
				lx_family_mapping[i].append(j)

	return lx_family_mapping


def main():

	# Parse options
	parser = OptionParser()
	parser.usage = "%prog [options]"
	parser.add_option("-C","", dest="config_file",type="str",
		help = "config file to specify decoders, corpus, target languages, duration, etc.")
	(options,args) = parser.parse_args()

	if (options.config_file == None):
		sys.stderr.write(sys.argv[0]+": -C config file not specified")
		sys.exit(-1)
	else:
		config_file = options.config_file

	if (len(args) !=0):
		parser.print_usage()
		sys.exit(-1)

        #----------------------------------------------
        ## load modules 
        # * datacfg for data config
        #----------------------------------------------
        mod_name, file_ext = os.path.splitext(os.path.split(config_file)[-1])
        datacfg = imp.load_source(mod_name,config_file)
        #----------------------------------------------

	lx_family_mapipng = get_lrfamily_idx(datacfg.trainlx,datacfg.lx_family)

	training = ( datacfg.training == 'True')
	test = (datacfg.test == 'True')

	if training:
		sys.stderr.write(sys.argv[0]+": Not to be used in training mode\n")
		sys.exit(-1)

	#####################
	## SPECIFY batchid ##
	#####################
	batchid = datacfg.batchid

	#############################
	## SPECIFY data and ssetid ##
	#############################
	ssetid_list = list()


        if test == True:
                datadir = datacfg.testdatadir
                for decoder in datacfg.decoder:
                        for corpus in datacfg.testcorpus:
                                for lx in datacfg.testlx:
                                        for dur in datacfg.testdur:
                                                ssetid_list.append(decoder+"-"+corpus+"-"+lx+"-"+dur)
                                                file_svmprob_base_list.append(datacfg.outputdir+"/"+decoder+"-"+corpus+"-"+lx+"-"+dur)

	for i in range(0,len(file_svmprob_base_list)):
	



	# read lrprob
	
	


def...

	
	try:
		fi_ref = open(file_ref,'r')
	except OSError:
		sys.stderr.write(sys.argv[0]+".get_lrfamily_idx(): Cannot open reference file\n")
		sys.exit(-1)

	ref_pattern = re.compile(r'(\S+)\s+(\S+)\s+(\S+).*')
	
	line = fi_ref.readline()
	if line == ''
		break
	line = line.rstrip('\n')
	
	m = re_pattern.search(line)
	if (m):
		LR_family = m.group(2)
		LR_exact = m.group(3)


	
	









if __name__ == '__main__':
	main()
