import os
from ij.io import OpenDialog, Opener
from ij import IJ

def getUniques(dataarray):
	array = []
	[array.append(i) for i in dataarray if i not in array]
	return array

op = OpenDialog("Choose Filepath Data...")
filepath = op.getDirectory()
newpath = filepath +'/RGB/'
os.mkdir(newpath)
filelist = os.listdir(filepath)
metadata = []
imgsdata = []
for i in filelist:
	if i.split('_')[-1] == 'Properties.xml':
		metadata.append(i)
	if i.split('.')[-1] == 'tif':
		imgsdata.append(i.split('_')[0])

imgsdata = getUniques(imgsdata)
metadata = getUniques(metadata)

for i in imgsdata:
	img00 = IJ.open(filepath + '/' + i + '_ch00.tif')
	img01 = IJ.open(filepath + '/' + i + '_ch01.tif')
	img02 = IJ.open(filepath + '/' + i + '_ch02.tif')
	IJ.run('Images to Stack', 'name=Stack title=[] use')
	IJ.run('8-bit')
	IJ.run('Stack to RGB')
	IJ.saveAs('Tiff', '%s' %(newpath + i + '_RGB.tif'))
	IJ.save()
	IJ.run('Close')
	IJ.run('Close')
	