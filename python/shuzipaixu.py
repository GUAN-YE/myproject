l=[]


for i in range(1,4):
   
    
    xx=input("请输入第%d个数:" % i)
    if xx.isdigit():
        l.append(xx)
    else:
        print("qinghsuru")
        break
        
        
        
l.sort()
print(l)