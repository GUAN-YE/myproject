from django.shortcuts import render
# from django.shortcuts import render_to_
from django.shortcuts import render_to_response
from django.http import HttpResponse








# Create your views here.



def login(request):
    if request.method=='GET':
        return render_to_response('first.html')
    else:
        
        
        name1=request.POST['name1'];
        name2=request.POST['name2'];
        name2=int(name2)
        name1=int(name1)
        if name1>=10 and name2<=10:
            var=name1-name2
            print(var)

            return HttpResponse({var:'var','status':0})
        else:
            return HttpResponse({'status':1})
