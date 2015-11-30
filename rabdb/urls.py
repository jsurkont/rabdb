from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'rabdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rabifier/', include('rabifier_app.urls', namespace='rabifier')),
    url(r'^browser/', include('browser.urls', namespace='browser')),
]
