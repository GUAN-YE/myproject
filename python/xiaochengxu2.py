i = int(input("请输入销售量："))
yi=int(100000)
er = int(200000)
si = int(400000)
liu = int(600000)
shi = int(1000000)
ti1=yi*0.1
ti2 = ti1 + yi*0.075
ti4 = ti2 + er*0.05
ti6= ti4 + er*0.03
ti10= ti6 + si*0.15


if (i < yi):
    
    print("提成为：",i*0.1)
    
elif (i<=er) and (i >yi):
    print("提成为：",(i-yi)*0.075+ti1)
elif  (i<=si) and (i >er):
    print("提成为：",(i-er)*0.05+ti2)
elif  (i<=liu) and (i >si):
    print("提成为：",(i-si)*0.03+ti4)

elif  (i>liu) and (i <= shi):
    print("提成为：",(i-liu)*0.015+ti6)
elif  (i>shi):
    print("提成为：",(i-shi)*0.01+ti10)