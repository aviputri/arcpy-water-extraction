from __future__ import print_function
import os
import arcpy
from arcpy.sa import *

inputdir = "D:/Avi/New simulation/DEM flood maps/clipped"
outputdir = inputdir + "/corrected"

for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently reclassifying {0}'.format(file))
		inp = inputdir+"/"+file
		outp = outputdir+"/"+file
		outReclass = Reclassify(inp, "Value", RemapValue([[0, 0], [1, 1], ["NODATA", 0]]))
		outReclass.save(outp)
		print('done!')
