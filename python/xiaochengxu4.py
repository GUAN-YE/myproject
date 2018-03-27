# l=[]
# con=1
# for i in range(30):
    
#     x=input("输入数第 %d 个数：" %con)
#     if x.isdigit():
#         con += 1
#         l.append(x)
#     else:
#         print("请输入数字！")
#         continue
    

    
    
# l.sort()
# print(l)
l = []
for a in range (100,1000):
    if (a/100%10)*3 + (a/10%10)*3 + (a%10)*3 == a:
        l.append(a)

print(l)
        
    