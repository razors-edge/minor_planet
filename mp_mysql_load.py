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
from jdcal import jd2gcal
from jdcal import MJD_0
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")
import MySQLdb

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def indices( mylist, value):
    return [i for i,x in enumerate(mylist) if x==value]

def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
#打印结果
homedir =  cur_file_dir()        
 
#homedir = os.getcwd()
#print homedir
configuration_file = homedir+'/configuration.dat'
configuration_file_dev = open(configuration_file,'rU')

lines1=configuration_file_dev.read().splitlines()
configuration_file_dev.close()

for line1 in lines1:
    word=line1.split()
#    print word
    if word[0] == 'user':
        user = word[2]
    elif word[0] == 'ip':
        ip = word[2]
    elif word[0] == 'mypassword':
        mypassword = word[2]

conn = MySQLdb.connect(host = ip,
                           user = user,
                           passwd = mypassword,
                           db = "catalogue")

cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
#print "server version:", row[0]
cursor.close ()

#inputfile = 'E:\\working\\Python\\minor_planet\\files\\AOOP_LongLat.txt'
#outputfileroot = 'E:\\working\\Python\\minor_planet\\files\\AOOP_LongLat_format'

inputfile = homedir+'/files/AOOP_LongLat.txt'
outputfileroot = homedir+'/files/AOOP_LongLat_format'

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
e.close()
#print name 
#print " name[0] ", name[0]
#print "name ",len(indices(name, name[0]))
ind_num = len(indices(name, name[0]))
for i in range(ind_num):
    print i
    mjd_lable  = str(int(float(mjd[i]) ))
    calendar_d = jd2gcal(2400000.5, float(mjd[i]))
    calendar_d_lable = ("%d%02d%02d" % (calendar_d[0],calendar_d[1],calendar_d[2])) 
#    print calendar_d_lable,float(mjd[i]),int(float(mjd[i])),calendar_d_lable
    outputfile = ("%s_%s.txt" % (outputfileroot,calendar_d_lable))
    h = open(outputfile,'w')
    try:
        for j in range(line_num/ind_num):
            h.write("%i %s %8.2f %s %s %s %s\n" % 
            (j+1,name[(j*ind_num)+i],float(mjd[(j*ind_num)+i]),lon[(j*ind_num)+i],
            lat[(j*ind_num)+i],dlon[(j*ind_num)+i],dlat[(j*ind_num)+i]))             
#    except Exception:
#        sys.stderr.write('读取文件发生IO异常！\n')
    finally:
        h.close()
#        sys.stderr.write('finnaly执行！\n')    
#        print "file closed"
    CurrentTable = ('aoop_longlat_%s'% calendar_d_lable)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS "+CurrentTable)
    cursor.execute("CREATE TABLE IF NOT EXISTS "+CurrentTable+
    "(IDNUM INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(IDNUM), " \
    "MPID VARCHAR(10), " \
    "MJD FLOAT(8,2), " \
    "LON FLOAT(10,6), "\
    "LAT FLOAT(10,6), " \
    "DLON FLOAT(10,6), "\
    "DLAT FLOAT(10,6) )")
    
    print "Table "+CurrentTable+" is created"
    cursor.close()
    cursor = conn.cursor()
#    time.sleep(20)
#    print "Load " + outputfile + " into " + CurrentTable
    loading_cmd = ("LOAD DATA LOCAL INFILE '" + outputfile + "' INTO TABLE " + CurrentTable + \
    " FIELDS TERMINATED BY ' ' ENCLOSED BY ' ' ")
    cursor.execute(loading_cmd)
    cursor.close()
        
print CurrentTable
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS "+CurrentTable)
cursor.close()
delta_t = datetime.datetime.now() - t0 
print delta_t 
     
print 'done'
