#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: views.py
@time: 2018/1/31 9:17
"""

from libs.utils import ajax
def index(request):
    return ajax.jsonp_fail(request, message=u'no path, what are you doing!')

def favicon(request):
    return ajax.jsonp_fail(request, message=u'favicon.ico is not a good path!')

def robots(request):
    return ajax.jsonp_fail(request, message=u'robots.txt is not a good path!')

def ads(request):
    return ajax.jsonp_fail(request, message=u'ads.txt is not a good path!')