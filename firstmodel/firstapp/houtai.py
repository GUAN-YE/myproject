# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection


import json


def houtai(request):
    jiaocai=request.POST.get('jiaocai')
    banben=request.POST.get('banben')
    curor=connection.curor()
    if jiaocai !='' and banben != '':
        sql="select * from goodmanage where goodsname='%s',goodsid='%s' "% (jiaocai,banben)      
    else:
        sql="select  * from goodmanage"
    allGoodMes=[]
    try:
        curor.execute(sql)
        for i in curor.fetchell():
            goods={
                'goodname':i[0],
                'goodid':i[1]
            }
            allGoodMes.append(goods)
        curor.close()
        return HttpResponse(json.dumps({'data':allGoodMes, 'status':'ok'}), content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({'data':allGoodMes, 'status':'error'}), content_type="application/json")

    
        
   
    

     # ce=request.POST.get('ce')
    # if jiaocai=="出版社" or banben=="版本":
        
    #     bb={'cc':'请选择出版社或版本'}
    #     return HttpResponse(json.dumps(bb))
    # else:

    #     aa={
    #         'jiaocai':'jiaocai',
    #         'banben':'banben',
    #         'ce':'ce'
    #     } 
    
    # ll=aa['jiaocai']
    return HttpResponse(json.dumps(aa),{'bb':ll})