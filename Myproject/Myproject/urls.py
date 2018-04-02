"""Myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from project.views import *
urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'ttt/',ttt),#测试页面显示接口
    url(r'projectadd/',projectadd),#课程添加接口
    url(r'courselist/',courselist),#课程列表界面
    url(r'orgshowApi/',orgshowApi),#培训机构数据展现接口
    url(r'coursedetail/',coursedetail),#课程详情展示界面
    url(r'coursedetailApi/',coursedetailApi),#课程详情展示接口
    url(r'procharpter/',procharpter),#课程章节展示界面
    url(r'procomment/',procomment),#课程评论显示界面
    url(r'projectshowApi',projectshowApi),#课程数据展现接口
    url(r'orgshow/',orgshow),#培训机构数据展现界面
    url(r'teacheradd/',teacheradd),#教师添加接口
    url(r'teacherlist/',teacherlist),#老师列表界面
    url(r'teadetail/',teadetail),#老师详情展示界面
    url(r'teadetailApi/',teadetailApi),#老师详情展示界面数据接口teaproApi
    url(r'teaproApi/',teaproApi),#老师详情展示界面课程数据接口
    url(r'teacherlistdetail/',teacherlistdetail),#老师详情界面
    url(r'orgadd/',orgadd),#培训机构添加接口
    url(r'orgdescript/',orgdescript),#培训机构详情介绍界面
    url(r'orgdetaildesc/',orgdetaildesc),#培训机构详情介绍界面
    url(r'orgprodesc/',orgprodesc),#培训机构课程介绍界面
    url(r'orgprodescApi/',orgprodescApi),#培训机构课程介绍数据接口
    url(r'orgteadesc/',orgteadesc),#培训机构老师详情介绍界面
    url(r'orgteadescApi/',orgteadescApi),#培训机构老师详情介绍界面数据接口
    url(r'teacherlistApi/',teacherlistApi),#老师列表界面
    url(r'orglistApi/',orglistApi),#老师详情界面
    url(r'main/',main),#用户主界面
    url(r'mainApi/',mainApi),#用户主界面数据展示接口
    url(r'mysource/',mysource),#个人中心课程展示界面
    url(r'mysourceApi/',mysourceApi),#个人中心课程展示界面数据接口
    url(r'mymessage/',mymessage),#我的消息展示界面
    url(r'personindex/',personindex),#个人中心展现页面
    url(r'personindexApi/',personindexApi),#个人中心展现页面
    url(r'registerApi/',registerApi),#用户注册数据接口
    url(r'register/',register),#用户注册界面
    url(r'loginApi/',loginApi),#用户注册界面
    url(r'forgetpwd/',forgetpwd),#忘记密码
    url(r'forgetpwdApi/',forgetpwdApi),#忘记密码
    url(r'^$',login),#用户登录页面端口  
]
