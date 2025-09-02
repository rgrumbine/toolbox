import sys
from math import *
import numpy as np
import copy

def rescale(tsi):
   tsi -= 1.5
   tsi /= 10
def unscale(tsi):
   tsi *= 10
   tsi += 1.5

length = 8
x1 = np.zeros((1,length))

#aa x1[0,0] = 16.644
#aa x1[0,1] = 16.618
#aa x1[0,2] = 16.657
#aa x1[0,3] = 16.759
#aa x1[0,4] = 16.887
#aa x1[0,5] = 16.919
#aa x1[0,6] = 16.924
#aa x1[0,7] = 16.966
#aa x1[0,8] = 17.040 
#arctic:
x1[0,0] = 5.190
x1[0,1] = 5.131
x1[0,2] = 5.088
x1[0,3] = 5.067
x1[0,4] = 4.998
x1[0,5] = 4.973
x1[0,6] = 4.960
x1[0,7] = 4.904

x1[0,0] = 14.826
x1[0,1] = 14.854
x1[0,2] = 14.973
x1[0,3] = 14.987
x1[0,4] = 15.000
x1[0,5] = 15.051
x1[0,6] = 15.047
x1[0,7] = 15.049
rescale(x1)

print(x1)

import tensorflow as tf

model = tf.keras.models.load_model("arctic_model.keras")
print(model.predict(x1))

fout = open("fout","w")
for i in range(0,365):
    y = model.predict(x1)
    for j in range(0,length-1):
      x1[0,j] = x1[0,j+1]
    x1[0,length-1] = y[0]

    z = y[0]
    unscale(z)
    print(i,z, file = fout)

