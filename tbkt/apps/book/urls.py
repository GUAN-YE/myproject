# coding: utf-8
from django.conf.urls import include, url, patterns

# 登录
urlpatterns = patterns('apps.book.views',
    (r"^select$", "p_select"),  #　选教材/教辅列表
    (r"^set$", "p_setbook"),  #　设置用户教材
    (r"^sources$", "p_sources"),  #　教材关联的所有教辅
)