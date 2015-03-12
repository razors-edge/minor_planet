from datetime import date, time, datetime, timedelta
import subprocess
def work():
  print "excuting mp code."
  task = "/home/catauser/PythonWorkspace/minor_planet/mp_cal_auto"
  subp1 = subprocess.Popen(task,stderr = subprocess.PIPE, stdout = subprocess.PIPE, shell = True)
  (exe_stdout1, _) = subp1.communicate()


def runTask(func,  hour=0, min=0, second=0):
  # Init time
  now = datetime.now()
  # print now.hour
  strnow = now.strftime('%Y-%m-%d %H:%M:%S')
  print "now:",strnow
  # First next run time
  set_time = str('%02d:%02d:%02d' % (hour,min,second))
  print set_time
  print "auto run in:",set_time
  while True:
      # Get system current time
      iter_now = datetime.now()
      run_time_h = iter_now.hour
      run_time_m = iter_now.minute
      run_time_s = iter_now.second
      iter_now_time = iter_now.strftime('%Y-%m-%d %H:%M:%S')
      print str(run_time_h),str(hour),str(run_time_m),str(min),str(run_time_s),str(second)
      if (str(run_time_h) == str(hour)) and (str(run_time_m) == str(min)) and (str(run_time_s) == str(second)):
          # Get every start work time
          print "start work: %s" % iter_now_time
          # Call task func
          func()
          print "task done."
          # Get next iteration time
          #iter_time = iter_now + period
          #strnext_time = iter_time.strftime('%Y-%m-%d %H:%M:%S')
          #print "next_iter: %s" % strnext_time
          # Continue next iteration
          continue

# runTask(work, min=0.5)
runTask(work, hour=13, min=50, second=0)
