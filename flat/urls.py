# -*- coding:utf8 -*-

from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^staffs$', views.record_list, name='record_list'),
    url(r'^staffs/(?P<id>\w*)$', views.record_detail, name='record_detail'),
    url(r'^export', views.export, name='export'),
    # url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
