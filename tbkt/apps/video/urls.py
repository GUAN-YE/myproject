#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: urls.py
@time: 2017/6/29 16:22
"""
from django.conf.urls import include, url, patterns

# 视频中心
urlpatterns = patterns('apps.video.views',
    (r"^tags$", "p_tags"),                              # 视频踩顶
    (r"^error_feedback$", "p_error_feedback"),          # 提交纠错
)