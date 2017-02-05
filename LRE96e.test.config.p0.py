#!/usr/bin/python

training = 'False'
test = 'True'

# About tools
tooldir = '/opt/status4/manualsys/tools'

# About training data
testdatadir = '/opt/status4/manualsys/data/mlf'
decoder = ('EN_fisher_v1nclip_24hctsalign_fbkz_n2',)
testcorpus = ('lre96e',)
testlx = ('all',)
testdur = ('30s',)

trainlx = ('ARegy','EName','ENsou','FAfar','FRcan','GEger','HIhin','JAjap','KOkor',
        'MAchn','MAtwn','SPcar','SPspa','TAtam','VIvie')

# Element for unique subset-id
ssetid = ('decoder','testcorpus','testlx','testdur')

# batchid (for training)
batchid = 'all-EN_fisher_v1nclip_24hctsalign_fbkz_n2-lre96d-'+testdur[0]

# Modeling
NG = '3'
is_sb = 'True'
df_option = '1norm'
idf_option = 'unsmoothed'

# About output
outputdir = './bos_df1norm_idfunsmoothed/p0'
lx_family = ('AR','EN','FA','FR','GE','HI','JA','KO','MA','SP','TA','VI')
ref = 'data/lre96_evaluation.ref'
hypout = outputdir+'/EN_fisher_v1nclip_24hctsalign_fbkz_n2-lre96e-all-30s.Model-all-EN_fisher_v1nclip_24hctsalign_fbkz_n2-lre96d-30s.score'


