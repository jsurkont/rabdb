from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'rabdb_sandbox.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rabifier/', include('rabifier.urls', namespace='rabifier')),
    url(r'^browser/', include('browser.urls', namespace='browser')),
]
