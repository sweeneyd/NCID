# -*- coding: utf-8 -*-
"""
Created on Sat Jan 24 17:08:05 2015

@author: Dan
"""

import NCID as nc
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

#=============================================================================
# Generate Image Process Data
#=============================================================================
ALDHpositive = nc.NCID(directory='/Users/Dan/Desktop/ALDH+RGB/', write2File=False)
ALDHnegative = nc.NCID(directory='/Users/Dan/Desktop/ALDH-RGB/', write2File=False)

#=============================================================================
# Fit Data to Normal Distribution
#=============================================================================
pCellsNC = [i[0][2] for i in ALDHpositive.cells]
nCellsNC = [i[0][2] for i in ALDHnegative.cells]
params_p = stats.norm.fit(pCellsNC)
params_n = stats.norm.fit(nCellsNC)
x = np.linspace(0, 0.4, 1001)
pdf_p = stats.norm.pdf(x, loc=params_p[0], scale=params_p[1])
pdf_n = stats.norm.pdf(x, loc=params_n[0], scale=params_n[1])
norm_pdf_p = pdf_p/max(pdf_p)
norm_pdf_n = pdf_n/max(pdf_n)

#=============================================================================
# Generate Violin Plot
#=============================================================================
plt.title('Fitted NC Ratio PDFs')
plt.plot(x, norm_pdf_n, 'r', x, norm_pdf_p, 'b')
plt.ylim([0, 1.1])
plt.xlabel('N/C Ratio')
plt.ylabel('Probablity Density')
plt.show()
#=============================================================================
# Generate Violin Plot
#=============================================================================
#sns.set(style="whitegrid")
#f, ax = plt.subplots(figsize=(11,6))
#sns.violinplot([pCellsNC, nCellsNC], color='Set3', bw = 0.2, cut = 0.6,
#               lw=0.5, innter='points', innter_kws={'ms':6})
#
#sns.despine(left=True, bottom=True)