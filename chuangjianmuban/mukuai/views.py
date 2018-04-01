from django.shortcuts import render,render_to_response

from django.http import HttpResponse
# from django.template import loader,Context


class person(object):
    def __init__(self,name,age,sex):
        self.name=name
        self.age=age
        self.sex=sex
    def say(self):
        return 'i am '+ self.name



def index(req):
    # ll= {
    #     'user':'ll','name':'jj','age':'22'
    # }
    ll=person('tom',23,'nan')
    er_list=['python','java','c']
   
    return render_to_response('index.html',{'lb':ll,'erlist':er_list})
# Create your views here.
