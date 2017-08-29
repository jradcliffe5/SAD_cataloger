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
rms_box=250
postfix = 'Taper'

def SAD_fit_remove(files,postfix):
    if os.path.isfile('catalogue.csv') == False:
        s = 'Catalog_name rms_{0} BMAJ_{0} BMIN_{0} BPA_{0} #_{0}      Peak_{0}    Dpeak_{0}     Flux_{0}    Dflux_{0}    RA---SIN_{0}   DEC--SIN_{0}  Dx_{0}      Dy_{0}       Maj_{0}     Min_{0}      PA_{0}    Dmaj_{0}    Dmin_{0}    Dpa_{0} #_{0}  MAJ-fit_{0} MIN-fit_{0} PA-fit_{0}    MAJ-dec_{0} MIN-dec_{0}  PA-dec_{0}  R_{0} MAJ-low_{0} MIN-low_{0}  PA-low_{0}    MAJ-hi_{0}  MIN-hi_{0}  PA-hi_{0}    Xpix_{0}   Ypix_{0}   MAXresid_{0}\n'.format(postfix)
        s = ' '.join(s.split())+'\n'
        s = s.replace(' ',',')
        os.system('touch catalogue_%s.csv' % postfix)
        text_file = open('catalogue_%s.csv' % postfix,'a')
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
os.system('rm catalogue_%s.csv detections.txt' % postfix)

detections = []
for file in os.listdir('./'):
    if file.endswith('IM_casa.fits'):
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
        try:
            BMAJ = hdu_list[0].header['BMAJ']/hdu_list[0].header['CDELT2']
            BMIN = hdu_list[0].header['BMIN']/hdu_list[0].header['CDELT2']
            BPA = hdu_list[0].header['BPA']
        except KeyError:
            print 'Run casa_convert.py first to get beam parameters into header'
            sys.exit()
        if len(lines) > 24:
            detections = detections + [file]
            open('%s_r.fitout' % file, 'w').writelines(file[:8]+'\n')
            open('%s_r.fitout' % file, 'a').writelines(str(rms)+'\n')
            open('%s_r.fitout' % file, 'a').writelines(str(BMAJ)+'\n')
            open('%s_r.fitout' % file, 'a').writelines(str(BMIN)+'\n')
            open('%s_r.fitout' % file, 'a').writelines(str(BPA)+'\n')
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
SAD_fit_remove(catalog_list,postfix)
os.system('rm *fitout')
