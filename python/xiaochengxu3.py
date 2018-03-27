import math


for i in range(100000):
    x=int (math.sqrt(i+100))#sqrt 开方
    y=int(math.sqrt(i+168))
    if (x*x==i+100) and (y*y==i+168):
        print ("x","y","i",x,y,i)
        
    