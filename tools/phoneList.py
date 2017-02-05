#!/usr/bin/python


##############################################
# (c) Raymond Ng 2016 University of Sheffield 
##############################################

import os
import re
import sys

class phoneList:


	def __init__(self,filename):
		"""Initialise phoneList"""
		self.filename = filename
		self.file = ''
		self.len = 0
		self.list = list()
		self.oovidx = -1
	
	def oovidx(self,oovidx):
		"""Explicitly define oov idx (default: -1)"""
		self.oovidx = oovidx

	def query(self):
		"""Print all members of the class"""
		print "filename: "+self.filename
		print "file: --"
		print "len: "+str(self.len)
		print "list: --"

	def load(self):
		# read phone list to get plist_len
		try:
			self.file = open(self.filename)
		except IOError:
			sys.stderr.write(sys.argv[0]+": Phone list file "+self.filename+" not found\n")
			sys.exit(-1)
	
		self.len = 0
		while True:
			line = self.file.readline()
			if (line == ''):
				break
			line = line.rstrip('\n')
			self.list.append(line)
			self.len += 1
		self.file.close()


	def vsmidx(self,word):
		try:
			return str(self.list.index(word)+1)
		except ValueError:
			return self.oovidx




