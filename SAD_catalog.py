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
### inputs ###
AIPS.userno = 1002
i=1
auto_rms = True
rms = 4.73189515179e-05
edge = 100
rms_box=400

def SAD_fit_remove(files):
    if os.path.isfile('catalogue.csv') == False:
        s = 'Catalog_name rms #      Peak    Dpeak     Flux    Dflux    RA---SIN   DEC--SIN   Dx      Dy       Maj     Min      PA    Dmaj    Dmin    Dpa #  MAJ-fit MIN-fit PA-fit    MAJ-dec MIN-dec PA-dec  R  MAJ-low MIN-low PA-low    MAJ-hi  MIN-hi  PA-hi    Xpix   Ypix   MAXresid\n'
        s = ' '.join(s.split())+'\n'
        s = s.replace(' ',',')
        os.system('touch catalogue.csv')
        text_file = open('catalogue.csv','a')
        text_file.write(s)
    for j in files:
        with open(j) as f:
            x = f.read().splitlines()
        remove = ['#','Component']
        for i in remove:
            x = [y for y in x if not i in y]
        x = [y for y in x if y != ' ']
        x = [y.lstrip() for y in x]
        x = ' '.join(x).replace('(',' ').replace(')',' ')
        x = ' '.join(x.split())
        text_file.write(x.replace(' ',',')+'\n')
os.system('rm catalogue.csv detections.txt')

detections = []
for file in os.listdir('./'):
    if file.endswith('IM.fits'):
        fitld = AIPSTask('FITLD')
        hduheader = pyfits.open(file)[0].header
        print file
        try:
            data = np.array(pyfits.open(file)[0].data[0,0,edge:edge+rms_box,edge:edge+rms_box])
        except IndexError:
            data = np.array(pyfits.open(file)[0].data[edge:edge+rms_box,edge:edge+rms_box])
        if auto_rms == True:
            rms = float(np.sqrt(np.mean(data**2)))
            print rms
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
        sad.dparm[1] = 6*rms
        sad.fitout = 'PWD:%s.fitout' % file
        sad.go()
        image.zap()
    	lines = open('%s.fitout' % file).readlines()
    	print len(lines)
    	if len(lines) > 24:
            detections = detections + [file]
            open('%s_r.fitout' % file, 'w').writelines(file+'\n')
            open('%s_r.fitout' % file, 'a').writelines(str(rms)+'\n')
            open('%s_r.fitout' % file, 'a').writelines(lines[18:])
    	os.system('rm %s.fitout' % file)

os.system('touch detections.txt')
thefile = open('detections.txt', 'w')
for item in detections:
  thefile.write("%s\n" % item)

catalog_list = []
for file in os.listdir('./'):
    if file.endswith('fitout'):
        catalog_list = catalog_list + [file]
SAD_fit_remove(catalog_list)
os.system('rm *fitout')

def substring(string_list):
    out=[]
    for s in string_list:
        if not any([s in r for r in string_list if s != r]):
            out.append(s)
    return out
'''
def make_SAD_catalogue(file):
    try:
        f = open(file,'rw+')
    except:
        print 'No sources detected'
    line = f.readlines()
    thing = ['Peak','Component','MAJ-fit']
    for i in thing:
        line = [x for x in line if i not in x]
    y = []
    x=[]

make_SAD_catalogue('catalogue.txt')
'''
