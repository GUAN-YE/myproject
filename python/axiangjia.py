from functools import reduce
tn=0
sn=[]
n=int(input(":::"))
a=int(input("sss:"))
for i in range(n):
    tn=tn+a;
    a=a*10
    sn.append(tn)
    print (tn)
sn=reduce(lambda x,y:x+y,sn)
print(sn)