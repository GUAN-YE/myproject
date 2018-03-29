# coding: utf-8
from django.conf.urls import include, url, patterns

# 照顾老版本语文，修改老接口保证参数、返回数据不变
urlpatterns = patterns('apps.task0810.views',
    (r"^sms$", "p_givesms"),  # 发短信作业
)