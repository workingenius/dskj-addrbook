from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^locaff/$', views.locaffs, name='locaffs'),
    url(r'^locaff/(?P<id>\w+)$', views.locaff, name='locaff'),
]
