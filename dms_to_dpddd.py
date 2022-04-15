
l1="46 45 16.4 - 48 46 32.1"
l2="46 47 18.3 - 48 01 17.6"
l3="46 32 32.7 - 48 28 26.3"
l4="46 28 18.8 - 48 28 57.0"

def dms_dpddd(line):
  words=line.split()
  lat = float(words[0]) + float(words[1])/60. + float(words[2])/3600.
  lon = float(words[4]) + float(words[5])/60. + float(words[6])/3600.
  lon = -lon
  #for i in range(0,8):
  #  print(i,words[i])
  return (lat, lon)

x = dms_dpddd(l1)
print("lat ",x[0], "lon ",x[1])
x = dms_dpddd(l2)
print("lat ",x[0], "lon ",x[1])
x = dms_dpddd(l3)
print("lat ",x[0], "lon ",x[1])
x = dms_dpddd(l4)
print("lat ",x[0], "lon ",x[1])
