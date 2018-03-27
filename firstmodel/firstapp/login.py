from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection


def login(request):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    if request.method=="GET":
        print(".............................")
        return render_to_response('login.html')
    else:
        print('0000000000000000000')
        Name=request.POST['userid']
        Password=request.POST['password']
        cursor=connection.cursor()
        sql="select * from usermanage where username='%s' and password='%s'"%(Name,Password)
        cursor.execute(sql)
        qq=cursor.fetchall()
        cursor.close()
        print("////////////////////")
        if qq:
            return render_to_response('houtai.html')
        else:
            return HttpResponse('zuowu')
            

        

