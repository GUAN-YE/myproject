# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse


import json

USER_DICT = {
        'k1':{'name':'jj','email':'jjjj@.com'},
        'k2':{'name':'dd','email':'jjjddj@.com'},
        'k3':{'name':'ff','email':'jjjjff@.com'},
    }
def biaodan(self):


    jj="dd"
    
    return render_to_response('xxx.html',{'USER_DICT':USER_DICT,'jj':jj})

# def login(request):
#     www='刘斌'
#     # nn = [1,2,3,4,5,6,7]
#     return render_to_response('houtai.html',{'name':www})

# def houtai(request):
#     jiaocai=request.POST.get('jiaocai')
#     banben=request.POST.get('banben')
#     # ce=request.POST.get('ce')
#     if jiaocai=="出版社" or banben=="版本":
        
#         bb={'cc':'请选择出版社或版本'}
#         return HttpResponse(json.dumps(bb))
#     else:

#         aa={
#             'jiaocai':'jiaocai',
#             'banben':'banben',
#             'ce':'ce'
#         } 
    
#     ll=aa['jiaocai']
    #     ww=models.ku.filter(jiaocai='jiaocai',banben='banben',ce='ce')
    #    for w in ww:
           

 
    return HttpResponse(json.dumps(aa),{'bb':ll})

  

