from __future__ import print_function
import os
import arcpy
from arcpy.sa import *

inputdir = "D:/Avi/New simulation/DEM flood maps"
outputdir = inputdir+"/clipped"

for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently clipping {0}'.format(file))
		name = str(os.path.splitext(file))
		outExtractByMask = ExtractByMask(inputdir+"/"+file, inputdir+"/model_boundary.shp")
		outExtractByMask.save(outputdir+"/"+file)
		print('done!')