import os, re, time, datetime, sys, math, fnmatch
from os.path import join, getsize
from datetime import date
from collections import deque
import Utilities
#from multiprocessing import Process	# No longer needed now SERPent is parallel
#from multiprocessing import Pool
from AIPS import AIPS, AIPSDisk
from AIPSTask import AIPSTask, AIPSList
from AIPSData import AIPSUVData, AIPSImage, AIPSCat
from Wizardry.AIPSData import AIPSUVData as WizAIPSUVData
import math, time, datetime
from numpy import *
import itertools
from time import gmtime, strftime, localtime
import pyfits
import numpy as np

AIPS.userno = 1002
i=1
auto_rms = True
rms = 4.73189515179e-05
edge = 100
rms_box=250
os.system('rm catalogue.txt detections.txt')
detections = []
for file in os.listdir('./'):
    if file.endswith('.fits'):
        fitld = AIPSTask('FITLD')
        hduheader = pyfits.open(file)[0].header
        data = np.array(pyfits.open(file)[0].data[0,0,edge:edge+rms_box,edge:edge+rms_box])
        if auto_rms == True:
            rms = float(np.sqrt(np.mean(data**2)))
        fitld.datain = 'PWD:%s' % file
        fitld.outname = str(i)
        fitld.outclass = 'IM'
        fitld.go()
        image = AIPSImage(str(i),'IM',1,1)
        sad = AIPSTask('SAD')
        sad.cparm[1:] = 8*rms, 6*rms, 5*rms
        sad.indata = image
        sad.in2data = image
    	sad.blc[1:] = edge,edge
    	sad.trc[1:] = int(hduheader['NAXIS1'])-edge,int(hduheader['NAXIS2'])-edge
        sad.dparm[1] = 5*rms
        sad.fitout = 'PWD:%s.fitout' % file
        sad.go()
        image.zap()
    	lines = open('%s.fitout' % file).readlines()
    	print len(lines)
    	if len(lines) > 24:
    		detections = detections + [file]
    		open('%s_r.fitout' % file, 'w').writelines(file)
    		open('%s_r.fitout' % file, 'a').writelines(lines[18:])
    	os.system('rm %s.fitout' % file)

os.system('touch detections.txt')
thefile = open('detections.txt', 'w')
for item in detections:
  thefile.write("%s\n" % item)
os.system('cat *fitout > catalogue.txt')
os.system('rm *fitout')
