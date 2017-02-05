#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import sys
import re
import subprocess
import imp
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

def print_lrscore(file_out,file_ref,hyp_list,lrprob):
	
        # write to output
        ref = np.genfromtxt(file_ref,dtype=str)

	# check lrprob size
	if lrprob.shape[1] != len(hyp_list):
		sys.stderr.write(sys.argv[0]+".print_lrscore: hyp_list and lrprob dimension mismatch\n")
		sys.exit(-1)

	len_sample = lrprob.shape[0]
	len_class = lrprob.shape[1]

	fmt_filename = np.tile(ref[:,0],(len_class,1)).T.reshape(1,len_sample*len_class)
	fmt_reflx = np.tile(ref[:,1],(len_class,1)).T.reshape(1,len_sample*len_class)
	fmt_hyplx = np.tile(hyp_list,(1,len_sample))
	# reshape left-to-right, then top-to-bottom
	fmt_lrprob = lrprob.reshape(1,len_sample*len_class)
	
	out_matrix = np.concatenate((fmt_filename,fmt_reflx,fmt_hyplx,fmt_lrprob)).T
	
	# write the matrix into a multi-column text file
	np.savetxt(file_out,out_matrix,delimiter=' ',fmt=['%s','%s','%s','%s'])






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

	
	if (len(args) != 0):
		parser.print_usage()
		sys.exit(-1)
	

        #----------------------------------------------
        ## load modules 
        # * datacfg for data config
        # * svm for svm_light wrappers
        #----------------------------------------------
        mod_name, file_ext = os.path.splitext(os.path.split(config_file)[-1])
        datacfg = imp.load_source(mod_name,config_file)
        svm = imp.load_source('svm',datacfg.tooldir+'/svm.py')
        #----------------------------------------------

	training = ( datacfg.training == 'True')
	test = (datacfg.test == 'True')

	if training:
		sys.stderr.write('Testing script does not accept config file for "Train"\n')
		sys.exit(-1)



        #######################
        ### SPECIFY batchid ###
        #######################
	batchid = datacfg.batchid


        ###############################
        ### SPECIFY data and ssetid ###
        ###############################
        ssetid_list = list()
        file_svmprob_base_list = list()

        if test == True:
                datadir = datacfg.testdatadir
                for decoder in datacfg.decoder:
                        for corpus in datacfg.testcorpus:
                                for lx in datacfg.testlx:
                                        for dur in datacfg.testdur:
                                                ssetid_list.append(decoder+"-"+corpus+"-"+lx+"-"+dur)
						file_svmprob_base_list.append(datacfg.outputdir+"/"+decoder+"-"+corpus+"-"+lx+"-"+dur)


        # test_svm
	if len(ssetid_list) != 1:
		sys.stderr.write("Not yet support multiple testing data files\n")
		sys.exit(-1)

	# for i in range(0,len(file_svmprob_base_list)):
	i=0
	try:
		os.remove(file_svmprob_base_list[i]+".lrprob")
	except OSError:
		pass

	TRAINMODEL_array = list()
	for thislx in datacfg.trainlx:
		TRAINMODEL_array.append(datacfg.outputdir+"/"+batchid+"."+thislx+".model")
		

	proc_svmtest_stdouterr = svm.test_svm('',
		datacfg.outputdir+"/"+ssetid_list[i]+".tfidf",
		TRAINMODEL_array,
		file_svmprob_base_list[i]+".lrprob")
	fo_testlog = open(datacfg.outputdir+'/'+ssetid_list[i]+'.test.log','a')
	fo_testlog.write(proc_svmtest_stdouterr)
	fo_testlog.close()

	#####################
	## Post-processing ##
	#####################
	lx_family_mapping = get_lrfamily_idx(datacfg.trainlx,datacfg.lx_family)

 	
	# load lrprob [Testsample-by-Targetclass]		
	lrprob = np.genfromtxt(file_svmprob_base_list[i]+".lrprob")
	lrfamily_prob = np.zeros([lrprob.shape[0],len(lx_family_mapping)])

	for k in range(0,len(lx_family_mapping)):
		lrfamily_prob[:,k] =  np.max(lrprob[:,lx_family_mapping[k]],axis=1)
	
	print_lrscore(datacfg.hypout,datacfg.ref,datacfg.lx_family,lrfamily_prob)



if __name__ == '__main__':
	main()
