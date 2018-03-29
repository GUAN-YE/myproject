#coding: utf-8
from django.conf import settings
from django.conf.urls import include, url, patterns

urlpatterns = patterns('',
    url(r'^apidoc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.APIDOC_DIR}),  # 接口文档
)

urlpatterns += patterns('',
    url(r'', include('apps.urls')),
)
