from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^staffs$', views.locaff_list, name='staff_list'),
    url(r'^staffs/(?P<id>\w*)$', views.locaff_detail, name='staff_detail'),
    url(r'^export', views.export, name='export'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

