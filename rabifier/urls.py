from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.search, name='search'),
    #url(r'^(?P<ticket>[a-z]+)/$', views.result, name='result'),
    #url(r'^search/$', views.search, name='search'),
    url(r'^(?P<ticket>[\w\-]+)/$', views.result, name='result'),
    #url(r'^done/$', views.result, name='result'),
    #url(r'^(?P<ticket>[0-9]+)/$', views.index, name='index'),
]
