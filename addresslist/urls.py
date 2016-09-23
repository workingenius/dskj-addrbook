from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^locaff/$', views.locaffs, name='locaffs'),
    url(r'^locaff/(?P<id>\w+)$', views.locaff, name='locaff'),
    url(r'^search$', views.search, name='search'),
    url(r'^all', views.all_locaffs, name='all'),
    url(r'^export', views.export, name='export'),
]
