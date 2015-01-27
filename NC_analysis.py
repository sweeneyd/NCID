# -*- coding: utf-8 -*-
"""
NOTE: if a ValueError: need more than 0 values to unpack appears:

cd Desktop
cd DirectoryWithImages
ls -a #if a '.DS_Store' file, or somehting similar is present...
rm .DS_Store

Created on Sat Jan 24 17:08:05 2015

@author: Dan
"""
import pylab
import NCID as nc
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau
import pandas as pd

#=============================================================================
# Generate Image Process Data
#=============================================================================
ALDHpositive = nc.NCID(root_directory='/Users/Dan/Desktop/ALDH+/', write2File=False)
ALDHnegative = nc.NCID(root_directory='/Users/Dan/Desktop/ALDH-/', write2File=False)

#=============================================================================
# Fit Data to Normal Distribution
#=============================================================================
# GET NC RATIOS
CUT = 0.05
pCellsNC = [i[0][2] for i in ALDHpositive.cells]
#pCellsNC.sort()
#pCellsNC = [pCellsNC[i] for i in range(int(np.ceil(CUT*len(pCellsNC))),
#                                       int(np.ceil((1-CUT)*len(pCellsNC))))]
 
nCellsNC = [i[0][2] for i in ALDHnegative.cells]
#nCellsNC.sort()
#nCellsNC = [nCellsNC[i] for i in range(int(np.ceil(CUT*len(nCellsNC))), 
#                                       int(np.ceil((1-CUT)*len(nCellsNC))))]
 
# GET Radii
pCellsR = [i[0][-2] for i in ALDHpositive.cells]
#pCellsV.sort()
#pCellsV = [pCellsV[i] for i in range(int(np.ceil(CUT*len(pCellsV))), 
#                                     int(np.ceil((1-CUT)*len(pCellsV))))]
 
nCellsR = [i[0][-2] for i in ALDHnegative.cells]
#nCellsV.sort()
#nCellsV = [nCellsV[i] for i in range(int(np.ceil(CUT*len(nCellsV))),
#                                     int(np.ceil((1-CUT)*len(nCellsV))))] 

#params_p = stats.norm.fit(pCellsNC)
#params_n = stats.norm.fit(nCellsNC)
#x = np.linspace(0, 0.4, 1001)
#pdf_p = stats.norm.pdf(x, loc=params_p[0], scale=params_p[1])
#pdf_n = stats.norm.pdf(x, loc=params_n[0], scale=params_n[1])

#=============================================================================
# Generate Violin Plot
#=============================================================================
#plt.title('Fitted NC Ratio PDFs')
#plt.plot(x, norm_pdf_n, 'r', x, norm_pdf_p, 'b')
#plt.ylim([0, 1.1])
#plt.xlabel('N/C Ratio')
#plt.ylabel('Probablity Density')
#plt.show()
#=============================================================================
# Generate Violin Plot
#=============================================================================
#sns.set(style="whitegrid")
#f, ax = plt.subplots(figsize=(11,6))
#sns.violinplot([pCellsV, nCellsV], color='Set3', bw = 0.2, cut = 0.6,
#               lw=0.5, innter='points', innter_kws={'ms':6})
#
#sns.despine(left=True, bottom=True)
#=============================================================================
# Generate Violin Plot
#=============================================================================
sns.set(style='ticks')
if len(nCellsR) == len(nCellsNC):
    nCellsR = pd.Series(nCellsR, name='R ALDH+ [m]')
    nCellsNC = pd.Series(nCellsNC, name='NC Ratio ALDH+')
    jp1 = sns.jointplot(nCellsR, nCellsNC,
                        kind='kde', stat_func=kendalltau,
                        color='#003758', xlim=(0, 100e-6), ylim=(0, 0.15))
#                        joint_kws={"gridsize": 50},
#                        marginal_kws={"bins": 50})
    pylab.savefig('/Users/Dan/Desktop/ALDH+.png')   
else:
    print 'ERROR: Something went terribly wrong...'
    

if len(pCellsR) == len(pCellsNC):
    pCellsR = pd.Series(pCellsR, name='R ALDH- [m]')
    pCellsNC = pd.Series(pCellsNC, name='NC Ratio ALDH-')
    jp2 = sns.jointplot(pCellsR, pCellsNC, 
                        kind='kde', stat_func=kendalltau,
                        color='#8D3B1A', xlim=(0, 100e-6), ylim=(0, 0.15))                        
#                        joint_kws={"gridsize": 50},
#                        marginal_kws={"bins": 50})
    pylab.savefig('/Users/Dan/Desktop/ALDH-.png')   
else:
    print 'ERROR: Something went terribly wrong...'
