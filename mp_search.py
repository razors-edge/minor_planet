# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 10:46:24 2012

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
from angular_distance import angular_distance
import re
from jdcal import gcal2jd
from jdcal import MJD_0
t0 = datetime.datetime.now()

def search_file(filename, search_path):
   """Given a search path, find file
   """
   file_found = 0
   paths = string.split(search_path, pathsep)
   for path in paths:
      if exists(join(path, filename)):
          file_found = 1
          break
   if file_found:
      return os.path.abspath(join(path, filename))
   else:
      return None

   # zone_definning.py - extract the zone number for search range
def search_box(racen, deccen, side_length):
    racen = float(racen)
    deccen = float(deccen)
    side_length = float(side_length)    

    # error trapping
    if (racen < 0.0) or (racen > 360.0):
        print  'RA out of range'
        return
    if (deccen < -90.0) or (deccen > 90.0):
        print 'DEC out of range'
        return
    if (side_length > 72000):
        print 'side length too large (20 degree maximum)'
        return
          
      
    #declination range
    if (deccen - (side_length/2)) > (-90.0):
        dec0 = (deccen - (side_length/2))
    else:
        dec0 = (-90.0)
    if (deccen + (side_length/2)) < (+90.0):
        dec1 = (deccen + (side_length/2)) 
    else:
        dec1 = (90.0)
 #   print 'dec1=',dec1
    
    #RA range (overly conservative)
    maxdec = abs(dec0) > abs(dec1)
    if (abs(dec0) > abs(dec1)):
        maxdec = abs(dec0)
    else:
        maxdec = abs(dec1)
    cosd = math.cos(maxdec/57.2958)
    if (cosd > (side_length/2.0)/180.):
        ra0 = ((racen-(side_length/2)/cosd) + 360.0) % 360.0
        ra1 = ((racen+(side_length/2)/cosd) + 360.0) % 360.0
    else: 
        ra0 = 0.
        ra1 = 360.
    
    print racen, ra0, ra1, deccen, dec0, dec1
    
    box_parameter = [racen, ra0, ra1, deccen, dec0, dec1]
    return box_parameter
#   end of zone_definning


if __name__ == '__main__':
#    print sys.argv  
    z=0
if not sys.argv[1:]:
    sys.argv += ["77.0","41.0","2014/10/29,15:21:30","200.0",'./mp.txt']

racen = sys.argv[1]
deccen = sys.argv[2]
search_daytime = sys.argv[3]
radius_m = sys.argv[4]
outputfile = sys.argv[5]

search_date = search_daytime.split(",")[0]
search_time = search_daytime.split(",")[1]
gcal_y =  search_date.replace("-","/").split("/")[0]
gcal_m =  search_date.replace("-","/").split("/")[1]
gcal_d =  search_date.replace("-","/").split("/")[2]
MJD_search_day = gcal2jd(gcal_y,gcal_m,gcal_d)[1]
mjd_search_lable = str(int(MJD_search_day))
gcal_h =  search_time.replace(":","/").split("/")[0]
gcal_min =  search_time.replace(":","/").split("/")[1]
if len(search_time.replace(":","/").split("/")) == 3:
    gcal_s =  search_time.replace(":","/").split("/")[2]
mjd_search_t = (float(gcal_h) + (float(gcal_min)/60.) + (float(gcal_s)/3600.) ) / 24.0

CurrentTable = ('aoop_longlat_%0s'% mjd_search_lable)
print "search MP from table: ",CurrentTable

g = open(outputfile,'w')

homedir = os.getcwd()
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


import MySQLdb
conn = MySQLdb.connect(host = ip,
                           user = user,
                           passwd = mypassword,
                           db = "catalogue")

                      
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
cursor.close ()

export_cmd = "SELECT max(DLON) , max(DLAT) FROM " + CurrentTable
cursor = conn.cursor()
cursor.execute(export_cmd)
match_result = cursor.fetchall()
cursor.close ()

max_dlon_d = match_result[0][0]
max_dlat_d = match_result[0][1]
d_t_d = mjd_search_t 
max_dlon = max_dlon_d * d_t_d
max_dlat = max_dlat_d * d_t_d
max_dang_dis = ang_dis = angular_distance(0, 0,max_dlon,max_dlat)
print max_dlon,max_dlat,max_dang_dis

side_length = (float(radius_m)/60.0)
box_parameter = search_box(racen, deccen, side_length)

ra_small = box_parameter[1] - abs(max_dlon)
ra_large = box_parameter[2] + abs(max_dlon)
dec_low = box_parameter[4] - abs(max_dlat)
dec_high = box_parameter[5] + abs(max_dlat)
#print ra_small,ra_large,dec_low,dec_high
if ra_small < ra_large:
    export_cmd1 = "  SELECT MPID , MJD, LON, LAT, DLON, DLAT FROM " + CurrentTable + " WHERE ((LON BETWEEN " + str(ra_small) + " AND " + str(ra_large) + " ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + "))"
else:
    export_cmd1 = "  SELECT MPID , MJD, LON, LAT, DLON, DLAT FROM " + CurrentTable + " WHERE (((LON BETWEEN 0 AND " + str(ra_large) + " ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + ") ) OR ((LON BETWEEN " + str(ra_small) + " AND 360.0 ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + ") ))"

cursor = conn.cursor()
cursor.execute(export_cmd1)
match_result1 = cursor.fetchall()
cursor.close()

g.write("MPID  MJD LON LAT DLON DLAT \n")

num_mp = 0
if len(match_result1) > 0:
    for k in range(len(match_result1)):
        mp_MPID_result =  match_result1[k][0]      
        mp_ra_result = match_result1[k][2] + (match_result1[k][4] * d_t_d)
        mp_dec_result = match_result1[k][3] + (match_result1[k][5] * d_t_d)
        mp_dra_result = match_result1[k][4]
        mp_ddec_result = match_result1[k][5]
#        print match_result1[k][2],match_result1[k][3],mp_ra_result,mp_dec_result
        ang_dis_cen2mp_result = angular_distance(float(racen), float(deccen),mp_ra_result,mp_dec_result)
#        print("%s   %10.7f %10.7f  %10.7f" % (match_result1[k][0],mp_ra_result,mp_dec_result,ang_dis_cen2mp_result))
        if (ang_dis_cen2mp_result < side_length):
            print("%s   %10.7f %10.7f  %0.2f %s %s" % (match_result1[k][0],match_result1[k][1],match_result1[k][2],match_result1[k][3],match_result1[k][4],match_result1[k][5]))
            g.write("%s   %10.7f %10.7f  %0.2f %s %s" % (match_result1[k][0],match_result1[k][1],match_result1[k][2],match_result1[k][3],match_result1[k][4],match_result1[k][5]))            
            num_mp = num_mp + 1
print "Number of knowen Minor Planet found: ", num_mp

g.close()
    
delta_t = datetime.datetime.now() - t0
print 'Time Spent: ',delta_t

 
#gcal_h = "%6.2f" % (now.hour+(now.minute/60.))
##search_t = float(gcal_h) / (24.0*step_d)/24.0*100
#search_t = float(gcal_h) * (1.0 / step_d ) / 24.0 * step_d * 100.0
#ind_num = int(1 / step_d)
#
#for i in range(ind_num):
#    mjd_h_start = int(i*step_d*100)
#    mjd_h_end = int((i+1)*step_d*100)
##    print mjd_h_start,mjd_h_end,search_t
#    if search_t >= mjd_h_start and search_t < mjd_h_end:
#        gcal_h_start = int(mjd_h_start * 24.0 / 100.0)
#        gcal_h_end = int(mjd_h_end * 24.0 / 100.0 )
#        gcal_min_start = int(((mjd_h_start * 24.0 / 100.0) - int(mjd_h_start * 24.0 / 100.0)) * 60)
#        gcal_min_end = int(((mjd_h_end * 24.0 / 100.0) - int(mjd_h_end * 24.0 / 100.0 )) * 60)
#        mjd_h_search_start = mjd_h_start
#        mjd_h_search_end = mjd_h_end
##        print mjd_h_search_start,search_t,mjd_h_search_end,gcal_h_start,gcal_h_end
#        
#MJD_today = gcal2jd(gcal_y,gcal_m,gcal_d)[1] 
#print "search window from ", gcal_y,"/",gcal_m,"/",gcal_d,",",gcal_h_start,":",gcal_min_start," to ", gcal_h_end,":",gcal_min_end
#CurrentTable = ('aoop_d0_longlat_%02d'% int(mjd_h_search_start))
#print "search MP from table: ",CurrentTable
#
#g = open(outputfile,'w')
#
#homedir = os.getcwd()
#configuration_file = homedir+'/configuration.dat'
#configuration_file_dev = open(configuration_file,'rU')
#
#lines1=configuration_file_dev.read().splitlines()
#configuration_file_dev.close()
#
#for line1 in lines1:
#    word=line1.split()
##    print word
#    if word[0] == 'user':
#        user = word[2]
#    elif word[0] == 'ip':
#        ip = word[2]
#    elif word[0] == 'mypassword':
#        mypassword = word[2]
#
#
#import MySQLdb
#conn = MySQLdb.connect(host = ip,
#                           user = user,
#                           passwd = mypassword,
#                           db = "catalogue")
#
#                      
#cursor = conn.cursor ()
#cursor.execute ("SELECT VERSION()")
#row = cursor.fetchone ()
#cursor.close ()
#
#export_cmd = "SELECT max(DLON) , max(DLAT) FROM " + CurrentTable
#cursor = conn.cursor()
#cursor.execute(export_cmd)
#match_result = cursor.fetchall()
#cursor.close ()
#
#max_dlon_d = match_result[0][0]
#max_dlat_d = match_result[0][1]
#d_t_d = (search_t - mjd_h_search_start) / 100.0 
#max_dlon = max_dlon_d * d_t_d
#max_dlat = max_dlat_d * d_t_d
#max_dang_dis = ang_dis = angular_distance(0, 0,max_dlon,max_dlat)
#print max_dlon,max_dlat,max_dang_dis
#
#side_length = (float(radius_m)/60.0)
#box_parameter = search_box(racen, deccen, side_length)
#
#ra_small = box_parameter[1] - abs(max_dlon)
#ra_large = box_parameter[2] + abs(max_dlon)
#dec_low = box_parameter[4] - abs(max_dlat)
#dec_high = box_parameter[5] + abs(max_dlat)
##print ra_small,ra_large,dec_low,dec_high
#if ra_small < ra_large:
#    export_cmd1 = "  SELECT MPID , MJD, LON, LAT, DLON, DLAT FROM " + CurrentTable + " WHERE ((LON BETWEEN " + str(ra_small) + " AND " + str(ra_large) + " ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + "))"
#else:
#    export_cmd1 = "  SELECT MPID , MJD, LON, LAT, DLON, DLAT FROM " + CurrentTable + " WHERE (((LON BETWEEN 0 AND " + str(ra_large) + " ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + ") ) OR ((LON BETWEEN " + str(ra_small) + " AND 360.0 ) and (LAT BETWEEN " + str(dec_low) + " AND "  + str(dec_high)  + ") ))"
#
#cursor = conn.cursor()
#cursor.execute(export_cmd1)
#match_result1 = cursor.fetchall()
#cursor.close()
#
#g.write("MPID  MJD LON LAT DLON DLAT \n")
#
#num_mp = 0
#if len(match_result1) > 0:
#    for k in range(len(match_result1)):
#        mp_MPID_result =  match_result1[k][0]      
#        mp_ra_result = match_result1[k][2] + (match_result1[k][4] * d_t_d)
#        mp_dec_result = match_result1[k][3] + (match_result1[k][5] * d_t_d)
#        mp_dra_result = match_result1[k][4]
#        mp_ddec_result = match_result1[k][5]
##        print match_result1[k][2],match_result1[k][3],mp_ra_result,mp_dec_result
#        ang_dis_cen2mp_result = angular_distance(float(racen), float(deccen),mp_ra_result,mp_dec_result)
##        print("%s   %10.7f %10.7f  %10.7f" % (match_result1[k][0],mp_ra_result,mp_dec_result,ang_dis_cen2mp_result))
#        if (ang_dis_cen2mp_result < side_length):
#            print("%s   %10.7f %10.7f  %0.2f %s %s" % (match_result1[k][0],match_result1[k][1],match_result1[k][2],match_result1[k][3],match_result1[k][4],match_result1[k][5]))
#            g.write("%s   %10.7f %10.7f  %0.2f %s %s" % (match_result1[k][0],match_result1[k][1],match_result1[k][2],match_result1[k][3],match_result1[k][4],match_result1[k][5]))            
#            num_mp = num_mp + 1
#print "Number of knowen Minor Planet found: ", num_mp
#
#g.close()
#    
#delta_t = datetime.datetime.now() - t0
#print 'Time Spent: ',delta_t
