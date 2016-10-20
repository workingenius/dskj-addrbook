from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^staffs$', views.locaff_list, name='staff_list'),
    url(r'^staffs/(?P<id>\w*)$', views.locaff_detail, name='staff_detail'),
    url(r'^export', views.export, name='export'),
]
