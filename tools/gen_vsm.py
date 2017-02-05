#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import sys
import re
import shutil
import subprocess
import imp
import numpy as np
from StringIO import StringIO
from optparse import OptionParser


def main():

	# Parse options
	parser = OptionParser()
	parser.usage = "%prog [options] <phone_list>"
	parser.add_option("-C","", dest="config_file",type="str",
			help = "config file to specify decoders, corpus, target langauges, duration, etc.")
	parser.add_option("--lbl",action="store_true",default=False, dest="isWriteLBL",
			help = "write out LBL file")
	parser.add_option("--checklre96d",action="store_true",default=False,dest="checklre96d",
			help = "Check the overlap (with test set) input from lre96d and remove")
	(options,args) = parser.parse_args()
	
	## Assign options
	if (options.config_file == None):
		sys.stderr.write(sys.argv[0]+": -C config file not specified")
		sys.exit(-1)
	else:
		config_file = options.config_file

	isWriteLBL = options.isWriteLBL
	checklre96d = options.checklre96d	
	
	if (len(args) != 1):
		parser.print_usage()
		sys.exit(-1)
	( file_phonelist , ) = args

        # read phone list to get plist_len
        try:
                plist_file = open(file_phonelist)
        except IOError:
                sys.stderr.write(sys.argv[0]+": Phone list file "+sys.argv[1]+" not found\n")
                sys.exit(-1)

        plist_len = 0
        for line in plist_file:
                plist_len += 1
        plist_file.close()


	
	#----------------------------------------------
	## load modules 
	# * datacfg for data config
	# * cal_tfidf for calculation of tfidf
	#----------------------------------------------
	mod_name, file_ext = os.path.splitext(os.path.split(config_file)[-1])
	datacfg = imp.load_source(mod_name,config_file)
       	cal_tfidf = imp.load_source('cal_tfidf',datacfg.tooldir+'/cal_tfidf.py')
	#----------------------------------------------


        # vector dimension for idf
        vector_len = 0
        for i in range(0,int(datacfg.NG)):
                if datacfg.is_sb == 'True':
                        vector_len += (plist_len+1)**(i+1)
                else:
                        vector_len += (plist_len)**(i+1)


	training = (datacfg.training == 'True') 
	test = (datacfg.test == 'True')

	#######################
	## oov in datacfg #####
	try:
		datacfg.has_oov
	except AttributeError:
		# has_oov field not defined, assumed false
		datacfg.has_oov = 'False'

	#######################
	### SPECIFY batchid ###
	#######################
	batchid = datacfg.batchid

	batch_df_vector = np.zeros(vector_len)
	batch_linenum = 0
	

	###############################
	### SPECIFY data and ssetid ###
	###############################
	ssetid_list = list()
	file_outprob_list = list()

	if training == True:
		datadir = datacfg.traindatadir
		for decoder in datacfg.decoder:
			for corpus in datacfg.traincorpus:
				for lx in datacfg.trainlx:
					for dur in datacfg.traindur:
						if os.path.isfile(datadir+'/'+decoder+"-"+corpus+"-"+lx+"-"+dur+".mlf"):
							ssetid_list.append(decoder+"-"+corpus+"-"+lx+"-"+dur)
							file_outprob_list.append(datacfg.outputdir+"/"+decoder+"-"+corpus+"-"+lx+"-"+dur+".tf")
						else:
							pass
	if test == True:
		datadir = datacfg.testdatadir
		for decoder in datacfg.decoder:
			for corpus in datacfg.testcorpus:
				for lx in datacfg.testlx:
					for dur in datacfg.testdur:
						if os.path.isfile(datadir+'/'+decoder+"-"+corpus+"-"+lx+"-"+dur+".mlf"):
							ssetid_list.append(decoder+"-"+corpus+"-"+lx+"-"+dur)
							file_outprob_list.append(datacfg.outputdir+"/"+decoder+"-"+corpus+"-"+lx+"-"+dur+".tf")
						else:
							pass
	##############################
	### Calculate lbl and prob ###
	##############################
	for j in range(0,len(ssetid_list)):
		ssetid = ssetid_list[j]
		file_outprob = file_outprob_list[j]
		# mlf2lbl ---------------------------------------
		fi_mlf = open(datadir+'/'+ssetid+'.mlf','r')

		# (optional check96d module to remove overlapped files)
		if checklre96d:
			filter_file=datacfg.lre96dremovelist
		else:
			filter_file='/dev/null'
		proc_lre96dcheck = subprocess.Popen([datacfg.tooldir+'/removeSegment.py',
			filter_file],
			stdin=fi_mlf,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(fi_mlf_checked,proc_lre96dcheck_stderr) = proc_lre96dcheck.communicate()
		fi_mlf.close()


		
		# mlf(checked)2lbl ---------------------------------
		# proc_mlf2lbl = subprocess.Popen([datacfg.tooldir+'/mlf2lbl.py',
		# 	file_phonelist], 
		#	stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		proc_mlf2lbl = subprocess.Popen([datacfg.tooldir+'/mlf2lbl.py',
			'--has_oov',datacfg.has_oov,
			file_phonelist], 
			stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(lbl,proc_mlf2lbl_stderr) = proc_mlf2lbl.communicate(input=fi_mlf_checked)
			
		if (proc_mlf2lbl_stderr != None and proc_mlf2lbl_stderr !=''):
			print "ERROR in mlf2lbl:"
			sys.stderr.write(proc_mlf2lbl_stderr)
			sys.exit(-1)
		if isWriteLBL:
			pass
			# decides what to do if writing out LBL files
			# sys.stdout.write(lbl)


		# lbl2prob -----------------------------------------
		proc_lbl2prob = subprocess.Popen([datacfg.tooldir+'/lbl2prob.py',
			'--ng',datacfg.NG,'--is_sb',datacfg.is_sb,
			'--df-option',datacfg.df_option,
			'--out-df',datacfg.outputdir+'/'+ssetid+'.df',file_phonelist], 
			stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(prob,proc_lbl2prob_stderr) = proc_lbl2prob.communicate(input=lbl)
			
		if (proc_lbl2prob_stderr != None and proc_lbl2prob_stderr !='' ):
			print "ERROR in lbl2proc"
			sys.stderr.write(proc_lbl2prob_stderr)
			sys.exit(-1)

		fo_outprob = open(file_outprob,'w')
		fo_outprob.write(prob)
		fo_outprob.close()

		if (training == True):
			(thislinenum, this_df_idx, this_df_count) = cal_tfidf.get_df(datacfg.outputdir+'/'+ssetid+'.df')
			batch_df_vector[this_df_idx] += this_df_count
			batch_linenum += thislinenum

	

	#########################
	### calculate df, idf ###
	###  (training only)  ###
	#########################
	if (training == True):	
	        # save batch-df
	        nz = np.nonzero(batch_df_vector != 0)
	        batch_df_svmfmt = batch_df_vector[nz]
	        batch_df_idx = nz[0]
	        

		# fo_batch_df = open(datacfg.outputdir+'/'+batchid+'.df','w')
		# for k in range(0,len(batch_df_idx)):
	        #         fo_batch_df.write(str(batch_df_idx[k]+1)+":"+str(batch_df_svmfmt[k])+" ")
	        # fo_batch_df.write("\nLINE:"+str(batch_linenum)+"\n")
	        # fo_batch_df.close()
		outdf_str = np.concatenate((np.add([batch_df_idx],1),
			np.tile([':'],(1,len(batch_df_idx))),
			[batch_df_svmfmt],
			np.tile([' '],(1,len(batch_df_idx)))
			)).reshape(4,len(batch_df_idx))
		np.savetxt(datacfg.outputdir+'/'+batchid+'.df',outdf_str.T.reshape(1,4*len(batch_df_idx)),fmt='%s',delimiter='')
		fo_batch_df = open(datacfg.outputdir+'/'+batchid+'.df','a')
		fo_batch_df.write("LINE:"+str(batch_linenum)+"\n")
	        fo_batch_df.close()
	
	        # calculate idf
		if (datacfg.idf_option == 'unsmoothed'):
		        (batch_idf_idx, batch_idf_svmfmt) = cal_tfidf.cal_idf(datacfg.outputdir+'/'+batchid+'.df',
		                datacfg.outputdir+'/'+batchid+'.idf')
		elif (datacfg.idf_option == 'smoothed'):
			(batch_idf_idx, batch_idf_svmfmt) = cal_tfidf.cal_smoothed_idf(
				datacfg.outputdir+'/'+batchid+'.df',
				datacfg.outputdir+'/'+batchid+'.idf',
				vector_len)
	        # fo_batch_idf = open(datacfg.outputdir+'/'+batchid+'.idf','w')

		### TO DO!! write idf in matrix!! ##        
		outidf_str = np.concatenate((np.add([batch_idf_idx],1),
			np.tile([':'],(1,len(batch_idf_idx))),
			[batch_idf_svmfmt],
			np.tile([' '],(1,len(batch_idf_idx)))
			)).reshape(4,len(batch_idf_idx))

		np.savetxt(datacfg.outputdir+'/'+batchid+'.idf',outidf_str.T.reshape(1,4*len(batch_idf_idx)),fmt='%s',delimiter='')
		
	        # fo_batch_idf = open(datacfg.outputdir+'/'+batchid+'.idf','w')
		# for k in range(0,len(batch_idf_idx)):
	        #         fo_batch_idf.write(str(batch_idf_idx[k]+1)+":"+str(batch_idf_svmfmt[k])+" ")
	        # fo_batch_idf.write("\n")
	        # fo_batch_idf.close()

	########################
	### Calculate tf-idf ###
	########################
	for j in range(0,len(ssetid_list)):
		######################
		### SPECIFY ssetid ###
		######################
		ssetid = ssetid_list[j]		

		file_inprob = datacfg.outputdir+"/"+ssetid+".tf"
		file_tfidf = datacfg.outputdir+"/"+ssetid+".tfidf"
						
		fi_inprob = open(file_inprob,'r')

		file_idf = batchid

	
		proc_tfidf = subprocess.Popen([datacfg.tooldir+'/cal_tfidf.py',
			'--ng',datacfg.NG,'--is_sb',datacfg.is_sb,
			'--idf',datacfg.outputdir+'/'+file_idf+'.idf',
			'--idf-option',datacfg.idf_option,
			file_phonelist], 
			stdin=fi_inprob,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(tfidf,proc_tfidf_stderr) = proc_tfidf.communicate()
		fi_inprob.close()

		if (proc_tfidf_stderr != None and proc_tfidf_stderr != ''):
			print "ERROR in cal_tfidf"
			sys.stderr.write(proc_tfidf_stderr)
			sys.exit(-1)
				
		fo_tfidf = open(file_tfidf,'w')
		fo_tfidf.write(tfidf)
		fo_tfidf.close()


	config_file_name = os.path.split(config_file)[-1]
	shutil.copy2(config_file,datacfg.outputdir)


if __name__ == '__main__':
	main() 
