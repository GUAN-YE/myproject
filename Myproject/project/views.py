from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import *
import time
import random
import json
import datetime
import time
import os



def randomString():
    for i in range(1,10):
        now_time=datetime.datetime.now().strftime("%Y%m%d%H%M%S");
        randomNum=random.randint(1,100);
        if randomNum < 0:
            randomNum=str(0)+str(randomNum);
        randomNumId=str(now_time) + str(randomNum);
    return randomNumId


def identificode(request):
    aaa = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','j','k','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','J','K','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    bg= (0 , 255 ,200)
    backcolor= (random.randint(32, 128), random.randint(32, 128), random.randint(32, 128))
    w = 60 * 4;
    h = 60
   
    image = Image.new('RGB', (w, h), (255,182,193))
    
    font = ImageFont.truetype(font='./shopApp/static/font/handan.ttf', size=36)
   
    draw = ImageDraw.Draw(image)
    
    for x in range(w):
        for y in range(h):
            draw.point((x, y),fill=bg)
   
    global xx;
    xx = "";
    for t in range(4):
        a=aaa[random.randint(0 , 57)];
        
        draw.text((60 * t + 10, 10), a, font=font,fill=backcolor)
        xx=xx+a;
    
    xx=str.lower(xx);
    image = image.filter(ImageFilter.BLUR)
  
    image.save('./project/static/myfile/code.jpg', 'jpeg')
    imgDic = {"imgPath":"static/myfile/code.jpg"}
    return HttpResponse(json.dumps(imgDic) , content_type = "application/json")


def  courselist(request):
    return render(request,"course-list.html")



def coursedetail(request):
    return render(request,"course-detail.html")


def coursedetailApi(request):
    for key in request.POST:
        projectname = request.POST.getlist(key)[0];
    print(projectname);
    sql = "select * from project where projectname = '%s'"%projectname;
    cursor = connection.cursor();
    cursor.execute(sql);
    a=cursor.fetchall();
    alldata=[];
    for row in a:
        mydata={
            'projectname':row[1],
            'propicture':row[2],
            'prodetail':row[3],
            'proteacher':row[4],
            'orgname':row[8],
            'orgpicture':row[9],
        }
        alldata.append(mydata);
    print(alldata)   
    return HttpResponse(json.dumps({'data':alldata}),content_type="application/json")



def projectshowApi(request):
    sql="select * from project"
    cursor=connection.cursor();
    cursor.execute(sql);
    allprojectTable=[]
    for row in cursor.fetchall():
        projectTable={
            'projectid':row[0],
            'projectname':row[1],
            'propicture':row[2],
            'prodetail':row[3],
            'proteacher':row[4],
            'orgname':row[8],
        }
        allprojectTable.append(projectTable)
    cursor.close();
    return HttpResponse(json.dumps({'data':allprojectTable,'status':'ok'}),content_type="application/json")



def procharpter(request):
    return render(request,"course-video.html");


def procomment(request):
    return render(request,"course-comment.html")



def teacherlist(request):
    return render(request,"teachers-list.html")



def teacherlistdetail(request):
    return render(request,"courselist.html")



def teacherlistApi(request):
    sql="select * from teacher"
    cursor=connection.cursor();
    cursor.execute(sql);
    allteacherTable=[]
    for row in cursor.fetchall():
        teacherTable={
            'teacherid':row[1],
            'teachername':row[2],
            'teachertype':row[3],
            'teacherdetail':row[4],
            'teacherimg':row[5],
            'teacherage':row[6],
            'orgname':row[7],
        }
        allteacherTable.append(teacherTable)
    cursor.close();
    return HttpResponse(json.dumps({'data':allteacherTable,'status':'ok'}),content_type="application/json")


def orglistApi(request):
    return render(request,"teachers-lists.html")

def teadetail(request):
    return render(request,"teacher-detail.html")


def teadetailApi(request):
    for key in request.POST:
        teachername=request.POST.getlist(key)[0];
    teachername = teachername.strip()
    sql="select * from teacher where teachername = '%s'"%teachername;
    cursor = connection.cursor();
    cursor.execute(sql);
    a=cursor.fetchall();
    print(a)
    allteacherTable=[];
    for row in a:
        teacherTable={
            'teacherid':row[1],
            'teachername':row[2],
            'teachertype':row[3],
            'teacherdetail':row[4],
            'teacherimg':row[5],
            'teacherage':row[6],
            'orgname':row[7],
        }
        allteacherTable.append(teacherTable);
    print(allteacherTable)
    return HttpResponse(json.dumps({'data':allteacherTable}),content_type="application/json")

def teaproApi(request):

    print(request.POST)
    for key in request.POST:
        teachername=request.POST.getlist(key)[0];

    teachername = teachername.strip()
   

    sql="select * from project where proteacher = '%s'"%teachername;
    cursor=connection.cursor();
    cursor.execute(sql);
    a=cursor.fetchall();
    print(a)
    allprojectTable=[]
    for row in a:
        projectTable={
            'projectid':row[0],
            'projectname':row[1],
            'propicture':row[2],
            'prodetail':row[3],
            'proteacher':row[4],
            'orgname':row[8],
        }
        allprojectTable.append(projectTable)
    cursor.close();
    return HttpResponse(json.dumps({'data':allprojectTable,'status':'ok'}),content_type="application/json")


def main(request):
    return render(request,"index.html")




def mainApi(request):
    return render(request,"index.html")


def registerApi(request):
    print("dddddddddddddddddddddddddddd")
    name=str(request.POST["username"]);
    pwd=str(request.POST["password"]);
    userid=randomString()
    userid=str(userid)
    print(type(userid));
    print(type(name));
    print(type(pwd));
    print(name,pwd,userid)
    cursor=connection.cursor();
    sql="insert into user (userid,username,password) values ('%s','%s','%s')" %(userid,name,pwd);
    cursor.execute(sql)
    print("******************************************")
    return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")




def register(request):
    return render(request,"register.html")


    

def loginApi(request):
    print("+++++++++++++++++++++++++++")
    name=request.POST["username"];
    pwd=request.POST["pwd"]; 
    cursor=connection.cursor();
    sql="select * from user where username ='%s' and password = '%s' "%(name,pwd);
    cursor.execute(sql);
    a=cursor.fetchall();
    print("-------------",a)
    cursor.close()
    if a:
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json");
    else:
        return HttpResponse(json.dumps({'status':'error'}),content_type="application/json");



def login(request):
    return render(request,"login.html")


def forgetpwd(request):
    return render(request,"forgetpwd.html")


def forgetpwdApi(request):
    username = request.POST["username"];
    password=request.POST["password"];
    sql="update user set password = '%s' where username = '%s'"%(password,username)
    try:
        cursor=connection.cursor();
        cursor.execute(sql);
        cursor.close()
        print("*******************************")
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({'status':'error'}),content_type="application/json")


添加接口
def projectadd(request):
    projectid=randomString();
    projectname=request.POST["projectname"];
    propicture=request.FILES["propicture"];
    prodetail=request.POST["prodetail"]
    proteacher=request.POST["proteacher"]
    charptertitle=request.POST["charptertitle"]
    charpter=request.POST["charpter"]
    charptercontent=request.POST["charptercontent"]
    propicturename=randomString()+".jpg";
    filepath = "./project/static/myfile/";
    filename=os.path.join(filepath,propicturename);
    filename=open(filename,'wb')
    filename.write(propicture.__dict__["file"].read());
    cursor=connection.cursor();
    sql="insert into project(projectid,projectname,propicture,prodetail,proteacher,charptertitle,charpter,charptercontent) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')"%(projectid,projectname,propicturename,prodetail,proteacher,charptertitle,charpter,charptercontent);
    cursor.execute(sql);
    print(projectname,propicturename,prodetail)
    return HttpResponse("dddddddddddd")




def teacheradd(request):
    teacherid=randomString();
    teachername=request.POST["teachername"];
    teacherimg=request.FILES["teacherimg"];
    teacherage=request.POST["teacherage"]
    teacherdetail=request.POST["teacherdetail"]
    orgname=request.POST["orgname"]
    teachertype=request.POST["teachertype"]
    orgpicturename=randomString()+".jpg";
    filepath = "./project/static/myfile/";
    filename=os.path.join(filepath,orgpicturename);
    filename=open(filename,'wb')
    filename.write(teacherimg.__dict__["file"].read());
    cursor=connection.cursor();
    sql="insert into teacher(teacherid,teachername,teacherimg,teacherage,teacherdetail,orgname,teachertype) VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(teacherid,teachername,orgpicturename,teacherage,teacherdetail,orgname,teachertype);
    cursor.execute(sql);
    print(teacherid,teachername,teacherimg,teacherage,teacherdetail,orgname,teachertype)
    return HttpResponse("dddddddddddd")



def personindex(request):
    return render(request,"personindex.html")


def personindexApi(request):
    for key in request.POST:
        userid = request.POST.getlist(key)[0];
    print(userid);
    cursor=connection.cursor();
    sql="select * from user where username = '%s'" % userid;
    cursor.execute(sql);
    a=cursor.fetchall();
    print(a)
    allmydata=[];
    for row in a:
        mydata={
            'username':row[1],
            'password':row[2],
            'telnumber':row[3],
            'useradress':row[8],
            'usersex':row[9],
            'birthday':row[10],
        }
        allmydata.append(mydata);
    print(allmydata)
    return HttpResponse(json.dumps({'data':allmydata}),content_type="application/json")


def updateperson(request):
    for key in request.POST:
        username = request.POST.getlist(key)[0];
        birthday = request.POST.getlist(key)[1];
        usersex = request.POST.getlist(key)[2];
        address = request.POST.getlist(key)[3];
        telnumber = request.POST.getlist(key)[4];
    print(userid,birthday,usersex,address,telnumber)
    cursor=connection.cursor();
    if birthday=="" and telnumber=="":
        sql="update user set usersex='%s' where username='%s'"%(usersex,username)
    if birthday!="" and telnumber=="":
        sql="update user set usersex='%s',birthday='%s' where username='%s'"%(usersex,birthday,username)
    if birthday=="" and telnumber!="":
        sql="update user set usersex='%s',telnumber='%s' where username='%s'"%(usersex,telnumber,username)
    cursor.execute(sql);
    cursor.close();
    return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")


def mysource(request):
    return render(request,"usercenter-mycourse.html")


def mysourceApi(request):
    for key in request.POST:
        username=request.POST.getlist(key)[0];
    print(username);
    sql="select * from user where username = '%s'"%username;
    cursor = connection.cursor();
    cursor.execute(sql);
    a=cursor.fetchall();
    allmydata=[];
    for row in a:
        mydata = {
            'projectid': row[4],
            'projectname': row[5],
            'projectpicture':row[6],
        }
        allmydata.append(mydata);
    print(allmydata);
    return HttpResponse(json.dumps({'data':allmydata}),content_type="application/json")


def mymessage(request):
    return render(request,"usercenter-message.html")

def orgadd(request):
    orgid=randomString();
    orgname=request.POST["orgname"];
    orgpicture=request.FILES["orgpicture"];
    orgdetail=request.POST["orgdetail"]
    orgteacher=request.POST["orgteacher"]
    projectname=request.POST["projectname"]
    orgpicturename=randomString()+".jpg";
    filepath = "./project/static/myfile/";
    filename=os.path.join(filepath,orgpicturename);
    filename=open(filename,'wb')
    filename.write(orgpicture.__dict__["file"].read());
    cursor=connection.cursor();
    sql="insert into org(orgid,orgname,orgpicture,orgdetail,orgteacher,projectname) VALUES ('%s','%s','%s','%s','%s','%s')"%(orgid,orgname,orgpicturename,orgdetail,orgteacher,projectname);
    cursor.execute(sql);
    print(projectname,orgpicture,orgdetail)
    return HttpResponse("dddddddddddd")


def orgshow(request):
    return render(request,"org-list.html")


def orgshowApi(request):
    sql="select * from org"
    cursor=connection.cursor();
    cursor.execute(sql);
    allorgTable=[]
    for row in cursor.fetchall():
        orgTable={
            'orgid':row[1],
            'orgname':row[2],
            'orgteacher':row[3],
            'orgdetail':row[5],
            'orgpicture':row[4],
            'projectname':row[6],
            'address':row[7],
        }
        allorgTable.append(orgTable)
    cursor.close();
    return HttpResponse(json.dumps({'data':allorgTable,'status':'ok'}),content_type="application/json")



def orgdetaildesc(request):
    return render(request,"orghomepage.html")


def orgprodesc(request):
    return render(request,"org-detail-course.html")


def orgprodescApi(request):
    print("+++++++++++++++++++++++++++++")
    for key in request.POST:
        orgname=request.POST.getlist(key)[0];
    print(orgname)
    sql="select * from project where orgname = '%s'"%orgname;
    cursor = connection.cursor();
    cursor.execute(sql);
    a=cursor.fetchall();
    allmydata=[];
    for row in a:
        mydata={
            'projectid':row[0],
            'projectname':row[1],
            'propicture':row[2],
            'prodetail':row[3],
            'proteacher':row[4],
            'orgname':row[8],
        }
        allmydata.append(mydata);
    print(allmydata);
    return HttpResponse(json.dumps({'data':allmydata}),content_type="application/json")


def orgteadesc(request):
    return render(request,"org-detail-teachers.html")


def orgdescript(request):
    return render(request,"org-detail-desc.html")


def orgteadescApi(request):
    for key in request.POST:
        orgname=request.POST.getlist(key)[0];
    sql="select * from teacher where orgname = '%s'"%orgname;
    cursor=connection.cursor();
    cursor.execute(sql);
    allteacherTable=[]
    for row in cursor.fetchall():
        teacherTable={
            'teacherid':row[1],
            'teachername':row[2],
            'teachertype':row[3],
            'teacherdetail':row[4],
            'teacherimg':row[5],
            'teacherage':row[6],
            'orgname':row[7],
        }
        allteacherTable.append(teacherTable)
    cursor.close();
    print(allteacherTable)
    return HttpResponse(json.dumps({'data':allteacherTable,'status':'ok'}),content_type="application/json")



def ttt(request):
    return render(request,"org-detail-desc.html")

