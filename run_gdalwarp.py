from __future__ import print_function
import os
from subprocess import call
call(["ls", "-l"])

inputdir = "D:/Avi/daily_flood_map"
#outputdir = "D:/Avi/New simulation/DEM flood maps/clip"
outputdir = inputdir
vmask = inputdir+"/model_boundary.shp"

for file in os.listdir(inputdir):
	if file.endswith(".tif"):
		print('Currently clipping {0}'.format(file))
		inp = inputdir+"/"+file
		outp = outputdir+"/clip_"+file
		print(inp)
		print(outp)
		srs = "EPSG:32652"
		driver = "GTiff"
		res = "5.0 -5.0"
		#cmd = 'gdalwarp -s_srs %s -t_srs %s -tr %s -tap -cutline %s -crop_to_cutline %s %s' % (srs, srs, res, vmask, inp, outp)
		#os.system(cmd)
		warp = 'gdalwarp -s_srs %s -t_srs %s -tr %s -tap -cutline %s -crop_to_cutline %s %s' % (srs, srs, res, vmask, inp, outp)
		call(warp)
