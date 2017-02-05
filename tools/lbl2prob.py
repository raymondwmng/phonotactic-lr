#!/usr/bin/python


##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import re
import sys
import imp
import numpy as np
from optparse import OptionParser


	

###########################
# MAIN
###########################
def main():

	# Parse options
	parser = OptionParser()
	parser.usage = "%prog [options] <phone_list>"
	parser.add_option("--out-df","",dest="df",
			help = "destination to save df file")
	parser.add_option("--ng","",dest="NG",default=2,
			help = "N-gram for document vector")
	parser.add_option("--nglbl","",dest="is_nglbl",default=False,
			help = "Label has been expanded to cover N-gram, thus implying --ng 1 here")
	parser.add_option("--is_sb","",dest="is_sb",default=False,
			help = "Add a single extra token to represent sentence start and setence end")
	parser.add_option("--df-option","",dest="df_option",default="1norm",
			help = "Options fof DF <1norm|2norm>")	
	(options,args) = parser.parse_args()


	if (options.df != None):
		df = options.df
	else:
		df = None
	
	
	

	# N-gram order
	NG = int(options.NG)
	is_nglbl = (options.is_nglbl == 'True')
	if ( is_nglbl ):		# Forced setting NG=1 if label already covers ng (nglbl)
		NG = 1

	# use sentence start and sentence end (label id = -1)
	is_sb = (options.is_sb == 'True')

	df_option = options.df_option

	if (len(args) != 1):
		# sys.stderr.write("Usage: cat *.lbl | "+sys.argv[0]+" phonelist > *.raw_prob\n")
		parser.print_usage()
		sys.exit(-1)
	( file_phonelist , ) = args	

	try:
		plist_file = open(file_phonelist)
	except IOError:
		sys.stderr.write(sys.argv[0]+": Phone list file "+sys.argv[1]+" not found\n")
		sys.exit(-1)

	plist_len = 0
	for line in plist_file:
		plist_len += 1	
	plist_file.close()



	# parse lbl
	lbl_file = sys.stdin
	# if (df != None):
	#	fo_df = open(df,'w')

	linenum = 0
	while True:
		line = lbl_file.readline()

		if (line == ''):
			break
		line = line.rstrip('\n')
	
		# construct integer list for lbl
		lbl_list = list()
		if is_sb:
			lbl_list.append(plist_len+1)	# reserved label for SENT_END
		# lbl_list.extend(map(int,line.lstrip(' ').rstrip(' ').split(' ')))
		lbl_list.extend(map(int,line.lstrip(' ').rstrip(' ').split()))

		if is_sb or len(lbl_list)==0:
			lbl_list.append(plist_len+1)

		# construct n-gram matrix
		lbl_2dlist = [[] for i in range(0,NG)]
		lbl_all_hist = [[] for i in range(0,NG)]
		
		# INCREMENTALLY construct shifted vector by circshift()
		#   i=0 1G
		#   i=1 2G ...
		for i in range(0,NG):
			lbl_2dlist[i] = np.roll(lbl_list,i)
			for j in range(0,i):
				# print "to cancel position "+str(j)+" at line "+str(i)
				lbl_2dlist[i][j] = 0
			lbl_matrix = np.matrix(lbl_2dlist[0:i+1][:])   # Note the index refers to (0:i) in matlab terms
		
			# construct identity vector for validity
			lbl_matrix_def = lbl_matrix.min(0)
			lbl_matrix_def[lbl_matrix_def != 0] = 1
			if (lbl_matrix.min(0).min() < 0):
				sys.stderr.write(sys.argv[0]+": lbl_matrix should contain only non-negative elements\n")
				sys.exit(-1)
				
			if is_sb:
				ng_count_vector = np.array([(plist_len+1)**j for j in range (0,i+1)])
			else:
				ng_count_vector = np.array([(plist_len)**j for j in range(0,i+1)])

			# N-GRAM COUNT VECTOR (for i^th-gram)
			lbl_vector_ng = np.multiply(ng_count_vector*(lbl_matrix-1)+1,lbl_matrix_def)
			
			if is_sb:	
				lbl_vector_hist, lbl_bin = np.histogram(lbl_vector_ng,bins=range(1,(plist_len+1)**(i+1)+2))
			else:
				lbl_vector_hist, lbl_bin = np.histogram(lbl_vector_ng,bins=range(1,(plist_len)**(i+1)+2))
			
			if (df_option == '1norm'):	
				lbl_vector_hist_nrm = lbl_vector_hist / np.sum(lbl_vector_hist, dtype=float)
			elif (df_option == '2norm'):
				lbl_vector_hist_nrm = lbl_vector_hist / np.sqrt(np.dot(lbl_vector_hist,lbl_vector_hist)) 
			
			# Concatenate all i-grams
			if i == 0:
				lbl_ngvec_hist_nrm = lbl_vector_hist_nrm	# normalised by sentence length
				lbl_ngvec_hist = lbl_vector_hist		# unnormalised
			else:
				lbl_ngvec_hist_nrm = np.concatenate((lbl_ngvec_hist_nrm,lbl_vector_hist_nrm))	# normed
				lbl_ngvec_hist = np.concatenate((lbl_ngvec_hist,lbl_vector_hist))		# un-normed
		# ----------------------------------------------------

		nz =  np.nonzero(lbl_ngvec_hist_nrm != 0)
		lbl_def_hist_nrm = lbl_ngvec_hist_nrm[nz]	# normed
		lbl_def_hist = lbl_ngvec_hist[nz]		# un-normed
		lbl_def_idx = nz[0]


		if ( df != None):
			try:
				lbl_alldf[nz] += 1
			except NameError:
				lbl_alldf = np.zeros(lbl_ngvec_hist_nrm.shape, dtype=int)
				lbl_alldf[nz] += 1

		# write out tf
		stdout_str = np.concatenate((np.add([lbl_def_idx],1).astype('|S32'),
			np.tile([':'],(1,len(lbl_def_idx))),
			np.array([lbl_def_hist_nrm]).astype('|S32'),
			np.tile([' '],(1,len(lbl_def_idx)))
			)).reshape(4,len(lbl_def_idx))
		np.savetxt(sys.stdout,stdout_str.T.reshape(1,4*len(lbl_def_idx)),
			fmt='%s',delimiter='')
		
		# for k in range(0,len(lbl_def_idx)):
		#	sys.stdout.write(str(lbl_def_idx[k]+1)+":"+str(lbl_def_hist_nrm[k])+" ")
		# sys.stdout.write("\n")
		linenum += 1	

	# write out df
	if (df != None): 
		nz = np.nonzero(lbl_alldf != 0)
		lbl_alldf_idx = nz[0]


		df_str = np.concatenate((np.add([lbl_alldf_idx],1).astype('|S32'),
			np.tile([':'],(1,len(lbl_alldf_idx))),
			np.array([lbl_alldf[lbl_alldf_idx]]).astype('|S32'),
			np.tile([' '],(1,len(lbl_alldf_idx)))
			)).reshape(4,len(lbl_alldf_idx))
		np.savetxt(df,df_str.T.reshape(1,4*len(lbl_alldf_idx)),
			fmt='%s',delimiter='')
		fo_df = open(df,'a')
		fo_df.write("LINE:"+str(linenum)+"\n")
		fo_df.close()

		## for k in (lbl_alldf_idx): fo_df.write(str(k+1)+":"+str(lbl_alldf[k])+" ")		
	lbl_file.close()

		
	

if __name__ == '__main__':
	main()	
