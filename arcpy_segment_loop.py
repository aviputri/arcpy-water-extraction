from __future__ import print_function
import os
import arcpy
from arcpy.sa import *

inputdir = "H:/TSX/k_db"
outputdir = "H:/TSX/seg_k_db"

# I separated the two processes, but I'm sure you can combine both if you want
#calculate statistics
for file in os.listdir(inputdir):
	if file.endswith(".tif"):
	    print('Currently calculating statistics of {0}'.format(file))
            #calculate statistics
            arcpy.CalculateStatistics_management(inputdir+"/"+file)
            print('done!')

#mean shift segment
for file in os.listdir(inputdir):
	if file.endswith(".tif"):
	    print('Currently segmenting {0}'.format(file))
	    seg_raster = SegmentMeanShift(inputdir+"/"+file,
                                          "20", "20", "20", "1 2 3")
	    seg_raster.save(outputdir+"/"+file)
	    print('done!')
