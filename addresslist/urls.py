from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^locaff/(?P<id>\w+)$', views.locaff, name='locaff'),
    url(r'^locaff_data/(?P<id>\w*)$', views.locaff_data, name='locaff_data'),
    url(r'^locaff/$', views.locaffs, name='locaffs'),
]
