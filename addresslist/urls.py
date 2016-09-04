from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^locaff/(?P<id>\w*)$', views.locaff, name='locaff'),
]
