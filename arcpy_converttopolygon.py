from __future__ import print_function
import os
import arcpy

inputdir = "H:/TSX/watermask_raster"
outputdir = "H:/TSX/watermask_poly"

for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently convertíng {0}'.format(file))
		name, daty = file.split('.')
		inp = inputdir+"/"+file
		outp = outputdir+"/"+name+".shp"
		arcpy.RasterToPolygon_conversion(inp, outp, "NO_SIMPLIFY", "value")
		print('done!')