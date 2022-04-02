from django.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import *

urlpatterns = [
    re_path(r'^crawl/$', crawl, name="crawl"),
    re_path(r'^recrawl/$', recrawl, name="recrawl"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)