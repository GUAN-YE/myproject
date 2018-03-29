# coding: utf-8
from django.conf.urls import include, url, patterns
from apps import views

urlpatterns = patterns('',
    url(r'^account/', include('apps.account.urls')),
    url(r'^book/', include('apps.book.urls')),
    url(r'^class/', include('apps.class.urls')),
    url(r'^gift/', include('apps.gift.urls')),
    url(r'^system/', include('apps.system.urls')),
    url(r'^task/', include('apps.task.urls')),
    url(r'^im/', include('apps.im.urls')),
    url(r'^video/', include('apps.video.urls')),
)

urlpatterns += patterns('apps.views',
    (r'^$', 'index'),
    (r'^favicon.ico$', 'favicon'),
    (r'^robots.txt$', 'robots'),
    (r'^ads.txt$', 'ads'),
)
