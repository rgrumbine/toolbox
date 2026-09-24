import os
import datetime

# Acquire basic data and average them
start = datetime.datetime(1980,1,1)
dt    = datetime.timedelta(1)
end   = datetime.datetime(2020,12,31)

ndays   = int((end-start)/dt + 1)
print('ndays = ',ndays, flush=True)

tag   = start
week = 0
while(tag <= end-7*dt ):
    print(tag, flush=True)
    if not os.path.exists('flx.'+tag.strftime("%Y%m%d")+'.nc'):
      print("missing ", 'flx.'+tag.strftime("%Y%m%d")+'.nc')

    if not os.path.exists('prs.'+tag.strftime("%Y%m%d")+'.nc'):
      print("missing ", 'prs.'+tag.strftime("%Y%m%d")+'.nc')
  
    tag += dt

