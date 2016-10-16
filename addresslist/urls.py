from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^all', views.locaff_list, name='all'),
    url(r'^export', views.export, name='export'),
]
