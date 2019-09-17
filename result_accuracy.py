import os
import lccrf
import sys

#locate the result and flood map directories
pathname1 = "D:/Avi/New simulation/result flood map/analysis/"
pathname2 = "D:/Avi/New simulation/daily flood maps/"
#uniquecharacters   = 0  # defines how many characters at the end of the string are unique. 

#matches = 0 
for item1 in os.listdir(pathname1):    
    for item2 in os.listdir(pathname2):
    	if item1.startswith(item2):
    	#if item1.startswith(item2[:-uniquecharacters]):
    		file = open('ACCURACY.txt', 'a')
    		sys.stdout = file
    		print(item1)
    		print(item2)
    		#break
    		ras1 = pathname1 + item1
    		ras2 = pathname2 + item2
    		arr1 = lccrf.read_img(TSXimage = ras1)
    		arr2 = lccrf.read_img(TSXimage = ras2)
    		lccrf.test_accuracy(test_array = arr1, gt_test_array = arr2)
    		m = (arr2 == 1).sum()
    		n = (arr2 == 0).sum()
    		totalpixel = m+n
    		print('True yes: {m}'.format(m=m))
    		print('True no: {n}'.format(n=n))
    		print('Total pixel: {totalpixel}'.format(totalpixel=totalpixel))
    		print(' ')
    		break