import os
def gogo(path):
    print("..............")
    for root,dicts,files in os.walk(path):
        for name in files:
            if name.endswith(".png") or name.endswith(".jpeg"):
                os.remove(os.path.join(root,name))
                print("shanchu:"+ os.path.join(root,name))

if __name__=='__main__':
    path = r'C:\Users\Administrator\Desktop\ww'
    gogo(path)
