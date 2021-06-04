from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from witswap.views import index, accept, balance


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accept/(?P<uuid>[^/]+)/', accept),
    url(r'^balance/(?P<uuid>[^/]+)/', balance),
    url(r'^', index),
]

handler500 = 'witswap.views.handler500'

urlpatterns += staticfiles_urlpatterns()

admin.site.site_header = 'WitSwap'
