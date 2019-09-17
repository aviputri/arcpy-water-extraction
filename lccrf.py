# Import the Python 3 print function
from __future__ import print_function

import pandas as pd
import geopandas as gpd
#from simpledbf import Dbf5 #use to read DBF files
from osgeo import gdal, gdal_array, ogr
import struct
import numpy as np
from sklearn.ensemble import RandomForestClassifier 
from sklearn.externals import joblib #use to save the model as .SAV
from sklearn.metrics import accuracy_score, confusion_matrix
import rasterio
from rasterio.transform import from_origin
from operator import itemgetter

# Tell GDAL to throw Python exceptions, and register all drivers
"""
By default the GDAL/OGR Python bindings do not raise exceptions when errors occur. 
Instead they return an error value such as None and write an error message to sys.stdout. 
You can enable exceptions by calling the UseExceptions() function
"""
gdal.UseExceptions()
gdal.AllRegister()

"""
If there are changes in the library, re-import the library with:
import imp
imp.reload(main)
"""

#read the class of each data sample
def read_class(tabular_data, gt_array_file):
	#tabular_data = 'the path of the DBF file', 
	#gt_array_file = 'the path of the output .npy file'
	#.npy = Numpy array file

	
	"""
	give an $id column (I scall it FID) to all your DBF file so you can call it in order when
	matching the feature class with the respective Reflectance (in extract_values).
	I gave the $id column in QGIS so there is no code line for that here.
	"""
	
	#read the DBF file
	table = gpd.read_file(tabular_data)
	#convert to pandas dataframe
	df = pd.DataFrame(table)

	#get Feature ID (FID) and Class ID (Id)
	class_id = df[['SID', 'GRIDCODE']] #[] == __getitem__ syntax

	#convert from Pandas dataframe into Numpy array
	a = class_id.values
	#sort based on FID (usually this is already sorted but better make it sure here)
	a = a[a[:,0].argsort(kind='mergesort')]
	#take out only the Class ID
	b = a[:,1]
	#convert into unsigned integer datatype
	b = b.astype(np.uint8)
	#make sure the Class ID array is flat
	gt_array = b.ravel()

	# save into .npy
	np.save(gt_array_file, gt_array) #gt_array save = '/location/array.npy'

	#output = gt_array
	return(gt_array)

#this extract 1 raster band at a time
#the next function will be used to stack all the resulting array layers into a 2D layer
def extract_values(rasterband, shp, raster):
	#rasterband = the number of band (unlike Python, GDAL indexing starts from 1)
	#shp = 'the path of the sample shapefile'
	#raster = 'the path of a band raster file'

	"""
	extract the FID with the Reflectance, sort it based on FID, then take only the Reflectance
	"""

	#open raster
	img_ds = gdal.Open(raster)
	gt = img_ds.GetGeoTransform()
	rb = img_ds.GetRasterBand(rasterband)
		
	#open shapefile
	ds = ogr.Open(shp)
	lyr=ds.GetLayer()
	li_values = list()
	for feat in lyr:
		geom = feat.GetGeometryRef()
		feat_id = feat.GetField('SID')
		mx,my=geom.GetX(), geom.GetY()  #coordinate in map units

		#Convert from map to pixel coordinates
		#Only works for geotransforms with no rotation
		px = int((mx - gt[0]) / gt[1]) #x pixel
		py = int((my - gt[3]) / gt[5]) #y pixel

		#extract the values one point at a time
		intval=rb.ReadAsArray(px,py,1,1)
		#append the values
		li_values.append([feat_id, intval[0]]) #this results in a list
		
		#sort the list by FID
		li_sort = sorted(li_values, key = itemgetter(0))

		#take out only the class ID (eliminate the FID)
		li_class = [row[1] for row in li_sort]

	src_ds = None
	img_ds = None

	return(li_class)

def stack_values(shp, raster, multibandfile):
	img_ds = gdal.Open(raster)
	
	a = img_ds.RasterCount
	c = list()
	for band in range(1,a+1): #using Python index
		b = extract_values(band, shp, raster)
		c.append(b)
		d = np.array(c).astype(gdal_array.GDALTypeCodeToNumericTypeCode
			(img_ds.GetRasterBand(band).DataType))
		multiband = d.reshape(-1,d.shape[1]).transpose()

	img_ds = None

	# save into .npy
	np.save(multibandfile, multiband) #save = '/location/array.npy'

	return(multiband)

#read the multispectral raster and covert it into Numpy array
def read_img(TSXimage):
	#TSXimage = path of the TSX image
	img_ds = gdal.Open(TSXimage, gdal.GA_ReadOnly)

	#initialize a 3D array -- use the size of our image for portability!
	img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount), 
		gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))

	#loop over all bands in dataset
	for band in range(img.shape[2]): #using GDAL index
		img[:,:,band] = img_ds.GetRasterBand(band+1).ReadAsArray()

	#you can check how many pixels were not zero using: (img > 0).sum()

	#flatten the array indo 2D (for RF input)
	multiband_array = img.reshape(-1,img.shape[2])
	#save the Numpy array
	#np.save(multiband_array_file, multiband_array)
	#return the img array
	return(multiband_array)	

#train the random forest and predict images
def train_rf(trees, train_multiband_array, train_class_array, model_sav):
	#trees = the number of Random Forest trees
	#maxfeatures = max number of features for the split (I chose None to not limit the features)
	#train_array = the band training sample in the form of Numpy array 
	#gt_array = the Class ID training sample in the form of Numpy array 
	#model_sav = 'the path of the saved Random Forest model'
	#img = the test sample in the form of Numpy array
	#result_array_file = 'the path of the prediction result in the form of Numpy array'

	rf = RandomForestClassifier(n_estimators = trees, min_samples_split = 10, 
		max_features = None, oob_score=False)
	rf = rf.fit(train_multiband_array, train_class_array)

	#print band importance
	a = train_multiband_array.shape[1]
	bands = list(range(1,a+1))

	for b, impo in zip(bands, rf.feature_importances_):
		print('Band {b} importance: {impo}'.format(b=b, impo=impo))

	return(rf)

def predict_rf(rf, img, result_array_file):
	#rf = the model returned from train_rf
	#img = the multiband array either from stack_values or read_img
	#result_array_file = path of the prediction result array

	
	result_array = rf.predict(img)
	#np.save(result_array_file, result_array)

	return(result_array)


#make raster file from the result
def rasterize(img_path, result_array, result_raster):
	#img_path = the path of the source raster
	#result_array = the prediction result in the form of Numpy array
	#result_raster = 'the path of the output raster'

	a = result_array.astype(np.uint8)

	#the origin of Rasterio is the coordinate of the Southwest edge of the raster file
	#this should be based on the source raster that is used
	#transform = from_origin(longitude, latitude, X resolution, Y resolution)
	#feel free to modify the long, lat, and resolutions

	#get the source raster origin (= the southwest corner of the raster)
	img = gdal.Open(img_path, gdal.GA_ReadOnly)
	trans = img.GetGeoTransform()
	xRes = trans[1]
	yRes = trans[5]
	xOrigin = trans[0]
	yOrigin = trans[3] + (img.RasterYSize)*yRes
	xSize = img.RasterXSize
	#close gdal dataset
	img = None
	#hence the raster origin
	transform = from_origin(xOrigin, yOrigin, xRes, yRes)

	#reshape Array into 2D
	b = np.reshape(a, (-1,xSize))
	c = np.flipud(b) #flip vertically
	#because rasterio writes from bottom to top

	#now define the CRS in rasterio (because GDAL's CRS is of different format, and IDK how to convert it w/o
	# including another library)
	imgras = rasterio.open(img_path)
	#take the CRS
	proj_init = imgras.crs
	#close the raster
	imgras.close()
	

	new_dataset = rasterio.open(result_raster, 'w', driver='GTiff',
		height = c.shape[0], width = c.shape[1],
		count=1, dtype=c.dtype,
		crs=proj_init,
		transform=transform)

	##from the old code, the CRS is in the PROJ4 format
	"""
		crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
	"""

	new_dataset.write(c, 1)
	new_dataset.close()

	#then call the extract_values function!!
	#output: test_array

def test_accuracy(test_array, gt_test_array):
	#year = the classification year
	#trees = the number of Random Forest trees
	#test_array = the prediction result in the form of Numpy array
	#rgt_test_array = the Class ID test sample in the form of Numpy array

	n_class = np.amax(gt_test_array)

	a = accuracy_score(gt_test_array, test_array)
	#b = confusion_matrix(gt_test_array, test_array, labels=list(range(1,n_class+1)))
	b = confusion_matrix(gt_test_array, test_array, labels=[1, 0])

	print('The overall accuracy is: {a}'.format(a=a))
	print(b)