#!/usr/bin/python

##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

# cat lre96d.overlap.scp | python removeSegment.py lre96d.30s.redudant.scp > lre96d.30s.non-overlap.mlf


import sys
import os
import re
import sys

#ivpath = os.environ['IVPATH']



#load the mappings file into a hash table
mydict = dict()
pattern = re.compile("(.*) \::\ (.*)")
#fm = open(fn_mappings)

fm = open(sys.argv[1])   #pass path to mapping as an arg
while True:
	line = fm.readline()
	if line=='':
		break
	line = line.rstrip('\n')   #chomp
	mydict[line] = line

#print mydict

#go through each line of corpus making replacements
#fi = open(fn_input)
fi = sys.stdin   #read from pipe

#fo = open(fn_output, 'w')
fo= sys.stdout
skipthisfile = 0

while True:
	line = fi.readline()
	if line=='':
		break
	line = line.rstrip('\n')   #chomp

	#first need to strip off and store STM tags
        mlfPattern = re.compile(r"\"(.*)\/(\S+)\.rec\"")
        m = mlfPattern.search(line)
        # result "skipthisfile" flag when there is a file argument
	if (m):
		filebasename = m.group(2)
                # print "FOUND FILELINE"+filebasename

		try:
			findbadfile = mydict[filebasename]
			skipthisfile = 1
		except KeyError:
			skipthisfile = 0
	if skipthisfile == 0:
		out = line
		fo.write(out+'\n')

fi.close()
fo.close()



