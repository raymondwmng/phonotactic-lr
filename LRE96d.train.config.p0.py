#!/usr/bin/python

training = 'True'
test = 'False'

# About tools
tooldir = '/opt/status4/manualsys/tools'

# About training data
traindatadir = '/opt/status4/manualsys/data/mlf/'
decoder = ('EN_fisher_v1nclip_24hctsalign_fbkz_n2',)
traincorpus = ('lre96d',)
# trainlx = ('ARegy','EName')
trainlx = ('ARegy','EName','ENsou','FAfar','FRcan','GEger','HIhin','JAjap','KOkor',
 	'MAchn','MAtwn','SPcar','SPspa','TAtam','VIvie')
traindur = ('30s',)

# must be used with --checklre96d in calling gen_vsm.py, otherwise ignored
# lre96dremovelist = '/share/spandh.ami1/lid/lib/flists/lre96d.30s.remove.scp'


# Element for unique subset-id
ssetid = ('decoder','traincorpus','trainlx','traindur')

# batchid
batchid = 'all-EN_fisher_v1nclip_24hctsalign_fbkz_n2-lre96d-'+traindur[0]

# Modeling
NG = '3'
is_sb = 'True'
df_option = '1norm'
idf_option = 'unsmoothed'

# About output
outputdir = './bos_df1norm_idfunsmoothed/p0'





