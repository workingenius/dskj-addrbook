from django.conf.urls import url
from . import views

urlpatterns = [
    url('^check_http_user_agent$', views.check_HTTP_USER_AGENT, name='check_HTTP_USER_AGENT'),
]

