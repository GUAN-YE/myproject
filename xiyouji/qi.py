# def repeat_twice(func):
#     def wrapper(*args, **kwargs):
#         func(*args, **kwargs)
#         print("you")
        
#     return wrapper

# @repeat_twice
# def foo():
#     print ("love")

# foo()
def foo_wrapper(func):
    def wrapper(*args, **kwargs):
        print ("。。。。。。。。。。。。。。。")  # 运行前
        print ('args: ', args, kwargs)
        res = func(*args, **kwargs)     # 这一行运行被装饰的原函数
        print ('finished!')           # 运行后
        return res
    return wrapper

@foo_wrapper
def foo(a, b):
    print (a + b)

foo(1, 2)