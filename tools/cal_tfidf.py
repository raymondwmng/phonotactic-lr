#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import sys
import re
import numpy as np
from optparse import OptionParser
from StringIO import StringIO 



# get_IDF
def get_idf(infile_idf):
	fi_idf = open(infile_idf,'r')
	# prob_pattern = re.compile(r'(\d+):([\d.]+)')

	# only 1 line
	line = fi_idf.readline()
	line = line.rstrip('\n').lstrip().rstrip()
	fi_idf.close()

	# m = prob_pattern.search(line)
	
	idf_data = np.genfromtxt(StringIO(line.replace(':',' ')),dtype=float)
	idf_idx = np.array(idf_data[np.arange(0,len(idf_data),2)]-1,dtype=int)
	idf_svmfmt = idf_data[np.arange(1,len(idf_data),2)]	

	return (idf_idx,idf_svmfmt)
	


# get_DF
def get_df(infile_df):
	
	fi_df = open(infile_df,'r')
	prob_pattern = re.compile(r'(\d+):(\d+)')
	line_pattern = re.compile(r'LINE:(\d+)')
	while True:
		line = fi_df.readline()
		if line == '':
			break
		line = line.rstrip('\n').lstrip().rstrip()
		
		m = line_pattern.search(line)

		if (m):
			linenum = int(m.group(1))
		else:	
			df_data = np.genfromtxt(StringIO(line.replace(':',' ')),dtype=int)		
			df_idx = df_data[np.arange(0,len(df_data),2)]-1
			df_count = df_data[np.arange(1,len(df_data),2)]
	fi_df.close()

	return (linenum, df_idx, df_count)

# cal_smoothed_IDF
def cal_smoothed_idf(infile_df,outfile_idf,vector_len):

	(linenum,df_idx,df_count) = get_df(infile_df)

	df_vector = np.zeros(vector_len)
	df_vector[df_idx] = df_count

	# Ref: Pyevolve (pyevolve.sourceforge.net)
	idf_svmfmt = np.log(linenum/np.float_(df_vector+1))
	
	# actually it is a full array
	return (range(0,len(idf_svmfmt)),idf_svmfmt)


# cal_IDF
def cal_idf(infile_df,outfile_idf):


	(linenum,df_idx,df_count) = get_df(infile_df)
	
	#### CALCULATE IDF FROM DF ####
	idf_svmfmt = np.log(linenum/np.float_(df_count))
	
	idf_idx = df_idx
	return (idf_idx,idf_svmfmt) 

######################
# MAIN
######################
def main():

	# Parse options
	parser = OptionParser()
	parser.usage = "%prog [options] <phone_list>"
	parser.add_option("--df","",dest="df",
			help = "file to read document frequency")
	parser.add_option("--idf","",dest="idf",
			help = "file to read inverse document frequency")
	parser.add_option("--idf-option","",dest="idf_option",default="unsmoothed",
			help = "Options to IDF <unsmoothed|smoothed>")
	parser.add_option("--out-idf","",dest="outidf",
			help = "file to write inverse document frequency")
        parser.add_option("--ng","",dest="NG",default=2,
                        help = "N-gram for document vector")
        parser.add_option("--is_sb","",dest="is_sb",default=False,
                        help = "Add a single extra token to represent sentence start and setence end")
	(options,args) = parser.parse_args()

	
	if (options.idf != None):
		isWriteIDF = False
		idf_file = options.idf
		if (options.outidf != None):
			sys.stderr.write(sys.argv[0]+": Cannot define --out-idf in read idf mode\n")
			sys.exit(-1)
	if (options.outidf != None):
		isWriteIDF = True
		idf_file = options.outidf
		if (options.idf != None):
			sys.stderr.write(sys.argv[0]+": Cannot define --idf in write idf mode\n")
			sys.exit(-1)

	NG = int(options.NG)
	is_sb = (options.is_sb == 'True')
	idf_option = options.idf_option

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


	# vector dimension for idf
	vector_len = 0
	for i in range(0,NG):
		if is_sb:
			vector_len += (plist_len+1)**(i+1)
		else:
			vector_len += (plist_len)**(i+1)

	# cal idf from df, or read from composed idf file
	if isWriteIDF:
		# calculate idf from df file
		if (idf_option == 'unsmoothed'):
			(idf_idx,idf_svmfmt) = cal_idf(options.df,options.outidf)
		elif (idf_option == 'smoothed'):
			(idf_idx,idf_smvfmt) = cal_smoothed_idf(options.df,options.outidf,vector_len)
		# output tfidf
		fo_idf = open(idf_file,'w')
		for k in range(0,len(idf_svmfmt)):
			fo_idf.write(str(idf_idx[k]+1)+":"+str(idf_svmfmt[k])+" ")
		fo_idf.write("\n")
		fo_idf.close()
	else:
		(idf_idx,idf_svmfmt) = get_idf(options.idf)
		
	idf_vector = np.zeros(vector_len)
	idf_vector[idf_idx] = idf_svmfmt		



	# modify tf-idf
	while True:
		line = sys.stdin.readline()
		if line == '':
			break
		line = line.rstrip('\n').lstrip().rstrip()

		# read the lengthy pattern
		tf_data = np.genfromtxt(StringIO(line.replace(':',' ')),dtype=float)
		tf_idx = np.array(tf_data[np.arange(0,len(tf_data),2)]-1,dtype=int)
		tf_prob = tf_data[np.arange(1,len(tf_data),2)]
	
	
		tf_vector = np.zeros(vector_len)
		tf_vector[tf_idx] = tf_prob

		
		################
		#### TF-IDF ####
		################
		tfidf_vector = tf_vector*idf_vector

		# svmfmt
		nz = np.nonzero(tfidf_vector != 0)
		tfidf_svmfmt = tfidf_vector[nz]
		tfidf_idx = nz[0]
	
		# normalisation
		tfidf_svmfmt = np.divide(tfidf_svmfmt,np.sum(tfidf_svmfmt))
	
		for k in range(0,len(tfidf_idx)):
			sys.stdout.write(str(tfidf_idx[k]+1)+":"+str(tfidf_svmfmt[k])+" ")
		sys.stdout.write("\n")
		


if __name__ == '__main__':
	main()	
		
	
