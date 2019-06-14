#from __future__ import print_function
import os
import arcpy
from arcpy.sa import *

inputdir = "D:/Avi/TSX Flood Mapping/HHVV/seg_k_db"
outputdir = "D:/Avi/TSX Flood Mapping/HHVV/isoclusterclass"

#I guess in ArcGIS 10.2 you cannot run the filename with +++ inside of the function so you have to
#declare it into a variable beforehand
#ArcGIS is also more sensitive to indents
for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently classifying {0}'.format(file))
		inp = inputdir+"/"+file
		outp = outputdir+"/class_"+file
		outUnsupervised = IsoClusterUnsupervisedClassification(inp, 6, 20, 10)
		outUnsupervised.save(outp)
		print('done!')