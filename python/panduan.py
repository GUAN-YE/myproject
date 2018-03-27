import string
s= input ("输入一段话：")
yingwen=0
kongge=0
shuzi=0
qita=0
for i in s:
    if i.isalpha():
        yingwen +=1
    elif i.isspace():
        kongge +=1
    elif i.isdigit():
        shuzi +=1
    else:
        qita +=1
print("yingwen=%d,kongge=%d,shuzi=%d,qita=%d" % (yingwen,kongge,shuzi,qita))