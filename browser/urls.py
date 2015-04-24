from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^annotation/(?P<protein_id>\S+)/$', views.details, name='details'),
    url(r'^tax/(?P<tax>\w*)/$', views.browse, name='browse'),
]
