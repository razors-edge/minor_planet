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
from jdcal import gcal2jd
from jdcal import MJD_0
from datetime import timedelta


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def aoop_input(inputfile,databasefile,output_eph,output_ll):        
    now = datetime.datetime.now()
    h = open(inputfile,'w')
    step_d = 6
    day_start = now
    day_end  = now + timedelta(days=step_d)
    
    gcal_y = "%i" % day_start.year
    gcal_m = "%i" % day_start.month
    gcal_d = "%i" % day_start.day    
    gcal_end_y = "%i" % day_end.year
    gcal_end_m = "%i" % day_end.month
    gcal_end_d = "%i" % day_end.day     
    MJD_today = gcal2jd(gcal_y,gcal_m,gcal_d)[1] 
    MJD_end = gcal2jd(gcal_end_y,gcal_end_m,gcal_end_d)[1] 
    print "from ", gcal_y,"/",gcal_m,"/",gcal_d," to ", gcal_end_y,"/",gcal_end_m,"/",gcal_end_d
#    print "from ", day_start, " to ", day_end 
    h.write("%i  %i  1\n" % (MJD_today, MJD_end))
    h.write("%s\n" % databasefile)
    # timezone = -8
    # altitude = 950
    # latitude = 40:23.6
    # longitude = 242:25.5
    h.write("117.575     40.393      950.0\n")
    h.write("%s\n" % output_eph)
    h.write("%s\n" % output_ll)
    h.close()

def run_exe_script(script_file_path,script_file_name,script_inputfile):    
    import subprocess    
    file_name = script_file_path+"/"+script_file_name+" "+script_inputfile
#    print file_name              
    subp1 = subprocess.Popen(file_name,
                            stderr = subprocess.PIPE, stdout = subprocess.PIPE, shell = True)
    (exe_stdout1, _) = subp1.communicate()
    time.sleep(2)
#    print type(exe_stdout1)
#    print exe_stdout1
    return exe_stdout1

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

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


if __name__ == '__main__':
#    print sys.argv  
    z=0
if not sys.argv[1:]:
    sys.argv += ["AOOP.input", "files/NEAm20150208.txt","files/AOOP_Eph.txt" ,"files/AOOP_LongLat.txt"]

inputfile = sys.argv[1]
databasefile = sys.argv[2]
output_eph = sys.argv[3]
output_ll = sys.argv[4]
#inputfile = "AOOP.input"
#databasefile = "files/NEA_20141025.txt"
#output_eph = "files/AOOP_Eph.txt"
#output_ll = "files/AOOP_LongLat.txt"
#print 'input',inputfile, databasefile, output_eph, output_ll
t0 = datetime.datetime.now()

aoop_input(inputfile,databasefile,output_eph,output_ll)

exepath = homedir
exename = 'AOOP'
#print exepath,exename,inputfile
output = run_exe_script(exepath,exename,inputfile)
#print output

delta_t = datetime.datetime.now() - t0 
print delta_t 
   

print 'done'
