import os
import sys
import datetime

#Script wanst to slog back in time
start = datetime.date(2021,12,31)

dt  = datetime.timedelta(-1)
end = datetime.date(2019,12,31)

stag = start.strftime("%Y%m%d")
send = end.strftime("%Y%m%d")

while (start >= end):
  tag  = start.strftime("%Y%m%d")
  #debug print(tag, flush=True)

  fname = "script_"+tag+".sh"
  if (os.path.exists(fname)): 
      print("already have script for "+tag, flush=True)
      start += dt
      continue
  if (os.path.exists("prod/"+tag)):
      print("already have tried for "+tag, flush=True)
      start += dt
      continue

  fout = open(fname, "w")

  fin = open("prefetch.head","r")
  for l in fin:
      print(l,end="",flush=True, file=fout)
  fout.flush()

  print("#PBS -N reget"+tag, file=fout)
  print("#PBS -o reget"+tag, file=fout)
  print("export  date="+tag, file=fout, flush=True)

  os.system("cat prefetch.tail >> "+fname)
  fout.flush()
  fout.close()
  os.system("qsub "+fname)
  os.system("sleep 120")

  start += dt

#debug: exit(0)

os.system("sleep 1200")

# Now submit the chaser:

fname = "script_"+stag+"t"+send+".sh"
fout = open(fname, "w")

fin = open("postfetch.head","r")
for l in fin:
    print(l,end="",flush=True, file=fout)
fout.flush()

print("#PBS -N post"+tag, file=fout)
print("#PBS -o post"+tag, file=fout)
print("export  date="+tag, file=fout, flush=True)
print("export start_date="+stag, file=fout)
print("export end_date="+send,  file=fout, flush=True)

os.system("cat postfetch.tail >> "+fname)
fout.flush()
fout.close()
os.system("qsub "+fname)
