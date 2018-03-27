test=int(input("输入成绩："))
if test>90 or test==90:
    fen="A"
elif test>60 or test==60:
    fen="B"
else:
    fen="C"
print("%d belong to %s" %(test,fen))#