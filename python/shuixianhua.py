for i in range(100,10000):
    q=i/100
    w=i/10%10
    k=i%10
    # print(q,w,k)
    if q*100+w*10+k==q**3+w**3+i**3:
        print("q:,w:,e:",q,w,k)
print("........")