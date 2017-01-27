from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^annotation/(?P<protein_id>\S+)/$', views.details, name='details'),
    url(r'^tax/(?P<tax>\w*)/sf/(?P<sf>\w*)/$', views.browse, name='browse'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/tax/(?P<tax>\d*)/sf/(?P<sf>\w*)/$', views.profile_result, name='profile_result'),
    url(r'^taxonomy/(?P<tax>\d*)/$', views.taxonomy, name='taxonomy'),
]
