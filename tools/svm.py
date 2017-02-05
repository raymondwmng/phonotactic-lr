#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import sys
import re
import subprocess
import linecache
import numpy as np
from optparse import OptionParser
from StringIO import StringIO

def train_svm(svmtooldir,TRAINTXT,TRAINMODEL):

	if (svmtooldir == None or svmtooldir == ''):
		# svmtooldir = '/share/spandh.ami1/sw/std/svm_light/v6.02/x86_64'
		svmtooldir = '/opt/spl/svm-light'

	proc_train = subprocess.Popen(['time',svmtooldir+'/svm_learn','-v','1',TRAINTXT,TRAINMODEL],
		stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	(proc_train_stdout,proc_train_stderr) = proc_train.communicate()

	trainsvm_out = "-"*80+"\n"
	trainsvm_out += "Training LR model from "+TRAINTXT+"\n"
	trainsvm_out += "<STDOUT>:\n"
	trainsvm_out += proc_train_stdout+"\n"
	trainsvm_out += "<STDERR>:\n"
	trainsvm_out += proc_train_stderr+"\n"
	
	trainsvm_out += "Time string: "+proc_train_stderr.split('\n')[0]+"\n"
	trainsvm_out += "-" * 80+"\n"

	return trainsvm_out 


def test_svm(svmtooldir,TESTTXT,TRAINMODEL,TESTRESULT):

	if (svmtooldir == None or svmtooldir == ''):
		# svmtooldir = '/share/spandh.ami1/sw/std/svm_light/v6.02/x86_64'
		svmtooldir = '/opt/spl/svm-light'

	if isinstance(TRAINMODEL,basestring):
		TRAINMODEL_array = [TRAINMODEL]
	else:
		TRAINMODEL_array = TRAINMODEL

	# do svm_classify individually
	for k in range(0,len(TRAINMODEL_array)):
		thismodel = TRAINMODEL_array[k]
		thislrprob = os.path.split(TESTRESULT)[0]+"/"+\
			os.path.split(TESTTXT)[1]+"."+\
			"model"+str(k)+".lrprob."+str(os.getpid())
		proc_test = subprocess.Popen(['time',svmtooldir+'/svm_classify','-v','1',
			TESTTXT,thismodel,thislrprob],
			stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(proc_test_stdout,proc_test_stderr) = proc_test.communicate()

		if k==0:
			testsvm_out = "-"*80+"\n"
		testsvm_out += "Testing "+thismodel+" on data from "+TESTTXT+"\n"
		testsvm_out += "<STDOUT>:\n"
		testsvm_out += proc_test_stdout
		testsvm_out += "<STDERR>:\n"
		testsvm_out += proc_test_stderr
		
		testsvm_out += "Time string: "+proc_test_stderr.split('\n')[0]+"\n"
		testsvm_out += "-"*80+"\n"

	# concatenate multiple output and remove temporary files
	if os.path.exists(TESTRESULT):
		os.remove(TESTRESULT)
	for k in range(0,len(TRAINMODEL_array)):
                thislrprob = os.path.split(TESTRESULT)[0]+"/"+\
			os.path.split(TESTTXT)[1]+"."+\
			"model"+str(k)+".lrprob."+str(os.getpid())
		if k == 0:
			cmd = 'paste -d" " '+thislrprob
		else:
			cmd += ' '+thislrprob
	cmd += ' > '+TESTRESULT
	subprocess.call(cmd,shell=True)
	
	for k in range(0,len(TRAINMODEL_array)):
		thislrprob = os.path.split(TESTRESULT)[0]+"/"+\
			os.path.split(TESTTXT)[1]+"."+\
			"model"+str(k)+".lrprob."+str(os.getpid())	
		os.remove(thislrprob)
	return testsvm_out

def main(): 
	pass



if __name__ == '__main__':
	main()
