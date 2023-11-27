import os
import sys
import datetime

#Script wanst to slog back in time
start = datetime.date(2022,10,16)

dt  = datetime.timedelta(-1)
end = datetime.date(2020,7,1)

stag = start.strftime("%Y%m%d")
send = end.strftime("%Y%m%d")
tag=stag

#Skip the prefetching -- all should already have been acquired or at least prefetched
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
