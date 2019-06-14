import arcpy
from arcpy.sa import *

seg_raster = SegmentMeanShift(inputfilepath, "20", "20", "20", "1 2 3")
seg_raster.save = (outputfilepath)