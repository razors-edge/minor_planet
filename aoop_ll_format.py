# -*- coding: utf-8 -*-
"""
Created on Mon May 05 12:20:33 2014

@author: han
"""

import sys, stat
import math
import subprocess as subp
## {{{ http://code.activestate.com/recipes/52224/ (r1)
from os.path import exists, join
import os.path
from os import pathsep
import string
import os
import datetime
import time
import re

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def indices( mylist, value):
    return [i for i,x in enumerate(mylist) if x==value]
        
def aoop_ll_format(inputfile,outputfileroot): 
    t0 = datetime.datetime.now()
    e=open(inputfile,'r')
    line_num = 0
    name = ['']
    mjd = ['']
    lon = ['']
    lat = ['']
    dlon = ['']
    dlat = ['']
    while True:
        line_in=e.readline()
        if not line_in: break
        if is_number(line_in.split()[1]) == True:
            name[line_num] = line_in.split()[0]
            mjd[line_num] = line_in.split()[1]
            lon[line_num] = line_in.split()[2]
            lat[line_num] = line_in.split()[3]
            dlon[line_num] = line_in.split()[4]
            dlat[line_num] = line_in.split()[5]
            name.append('')
            mjd.append('')
            lon.append('')
            lat.append('')
            dlon.append('')
            dlat.append('') 
            line_num = line_num + 1                           
    name.pop()
    mjd.pop()
    lon.pop()
    lat.pop()
    dlon.pop()
    dlat.pop()
    
    ind_num = len(indices(name, name[0]))
    for i in range(ind_num):
        outputfile = ("%s_%02d.txt" % (outputfileroot,i))
        h = open(outputfile,'w')
        for j in range(line_num/ind_num):
            h.write("%i %s %s %s %s %s %s\n" % 
            (j+1,name[(j*ind_num)+i],mjd[(j*ind_num)+i],lon[(j*ind_num)+i],
            lat[(j*ind_num)+i],dlon[(j*ind_num)+i],dlat[(j*ind_num)+i]))             
        h.close()    
    e.close()

    delta_t = datetime.datetime.now() - t0 
    print delta_t 
    return     

aoop_ll_format('E:\\working\\Python\\minor_planet\\files\\AOOP_LongLat.txt',
               'E:\\working\\Python\\minor_planet\\files\\AOOP_LongLat_format')   
     
print 'done'
