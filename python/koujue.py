import sys#系统文件
sys.stdout.write(chr(1))
sys.stdout.write(chr(1))#标准输出
print("  ")
for i in range(1,11):
    sys.stdout.write(chr(219))#ord()函数主要用来返回对应字符的ascii码，chr()主要用来表示ascii码对应的字符他的输入时数字，可以用十进制，也可以用十六进制。
    sys.stdout.write(chr(219))
print(" ")