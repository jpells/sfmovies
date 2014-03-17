from django.conf.urls import patterns, include, url
from django.contrib import admin
from films.views import FilmsJsonView, IndexTemplateView
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^films/', FilmsJsonView.as_view(), name='films'),
    url(r'^$', IndexTemplateView.as_view(template_name="films/index.html")),
)