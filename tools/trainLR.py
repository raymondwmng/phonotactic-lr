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
        # * svm for svm_light wrapper
        #----------------------------------------------
        mod_name, file_ext = os.path.splitext(os.path.split(config_file)[-1])
        datacfg = imp.load_source(mod_name,config_file)
        svm = imp.load_source('svm',datacfg.tooldir+'/svm.py')
        #----------------------------------------------

	training = (datacfg.training == 'True')
	test = (datacfg.test == 'True')

	if test:
		sys.stderr.write('Training script does not accept config file for "Test"\n')
		sys.exit(-1)


	##########################################
	## harcoded strlen for language family ###
	##########################################
	try:
		if (datacfg.train_dialect == 'True'):
		        # lxfamily string len : hardcoded to be 2 here
		        lxfamily_strlen = 5
		else:
			lxfamily_strlen = 2
        except AttributeError:
		lxfamily_strlen = 2


        #######################
        ### SPECIFY batchid ###
        #######################
        batchid = datacfg.batchid


        ###############################
        ### SPECIFY data and ssetid ###
        ###############################
        ssetid_list = list()

        if training == True:
                datadir = datacfg.traindatadir
                for decoder in datacfg.decoder:
                        for corpus in datacfg.traincorpus:
                                for lx in datacfg.trainlx:
                                        for dur in datacfg.traindur:
						if os.path.isfile(datacfg.outputdir+"/"+decoder+"-"+corpus+"-"+lx+"-"+dur+".tfidf"):
	                                                ssetid_list.append(decoder+"-"+corpus+"-"+lx+"-"+dur)
						else:
							pass
	

        # train_svm
        for thislx in datacfg.trainlx:
                try:
                        os.remove(datacfg.outputdir+"/"+batchid+"."+thislx+".train.txt")
                except OSError:
                        pass

                for k in range(0,len(ssetid_list)):
                        ssetid2 = ssetid_list[k]
                        thislx2 = ssetid2.split('-')[-2]
                        file_tfidf = datacfg.outputdir+"/"+ssetid2+".tfidf"

                        if thislx == thislx2:
                                cmd = "cat "+file_tfidf+ \
                                " | gawk '{print \"1 \"$0}' >> "+ \
                                datacfg.outputdir+"/"+batchid+"."+thislx+".train.txt"
                                subprocess.call(cmd,shell=True)
                        else:
				if (thislx[0:lxfamily_strlen] != thislx2[0:lxfamily_strlen]):	# only take languages from different language family 
	                                cmd = "cat "+file_tfidf+ \
        	                        " | gawk '{print \"-1 \"$0}' >> "+ \
                	                datacfg.outputdir+"/"+batchid+"."+thislx+".train.txt"
                        	        subprocess.call(cmd,shell=True)
				else:
					pass

                proc_svmtrain_stdouterr = svm.train_svm('',
                        datacfg.outputdir+"/"+batchid+"."+thislx+".train.txt",
                        datacfg.outputdir+"/"+batchid+"."+thislx+".model")

                # seems problems with "a" flag
                fo_trainlog = open(datacfg.outputdir+'/'+batchid+'.train.log','a')
                fo_trainlog.write(proc_svmtrain_stdouterr)
                fo_trainlog.close()

                os.remove(datacfg.outputdir+"/"+batchid+"."+thislx+".train.txt")





if __name__ == '__main__':
	main()
