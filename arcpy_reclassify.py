from __future__ import print_function
import os
import arcpy
from arcpy.sa import *

inputdir = "H:/TSX/isoclusterclass"
outputdir = "H:/TSX/watermask_raster"

for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently reclassifying {0}'.format(file))
		inp = inputdir+"/"+file
		outp = outputdir+"/water_"+file
		outReclass = Reclassify(inp, "Value", RemapValue([[1, "NODATA"], [2, "NODATA"], [3, 1]]))
		outReclass.save(outp)
		print('done!')
