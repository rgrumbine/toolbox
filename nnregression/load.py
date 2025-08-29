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

length = 9

x1 = np.zeros((1,length))

x1[0,0] = 16.644
x1[0,1] = 16.618
x1[0,2] = 16.657
x1[0,3] = 16.759
x1[0,4] = 16.887
x1[0,5] = 16.919
x1[0,6] = 16.924
x1[0,7] = 16.966
x1[0,8] = 17.040 

rescale(x1)

print(x1)

import tensorflow as tf

model = tf.keras.models.load_model("first_model.keras")
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

