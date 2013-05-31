from django.conf.urls.defaults import *
from parblog import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    (r'^$', 'parblog.view.index.index'),
    (r'^comment/post/?$', 'parblog.view.index.comment_post'),
    (r'^rss/?$', 'parblog.view.index.rss'),
    (r'^robots.txt$', 'parblog.view.index.robots'),
    (r'^sitemap.xml$', 'parblog.view.index.sitemap'),        
    
    (r'^admin/$', 'parblog.view.admin.index.index'),
    (r'^admin/preview/549284/(?P<page_slug>[^/]+)/$', 'parblog.view.admin.index.preview'),
    (r'^admin/entry/$', 'parblog.view.admin.index.entry'),
    (r'^admin/images/$', 'parblog.view.admin.index.images'),
    (r'^login/$', 'parblog.view.admin.index.login'),
    (r'^logout/$', 'parblog.view.admin.index.logout'),
    
    (r'^google18fc456a29576b6a.html$', 'parblog.view.index.goog'),
    
    (r'^tag/(?P<tag_slug>[^/]+)/?$', 'parblog.view.index.tag'),
    (r'^(?P<year>[\d]+)/(?P<month>[\d]+)/?$', 'parblog.view.index.archive'),
    (r'^(?P<page_slug>[^/]+)/?$', 'parblog.view.index.page'),
    
    
    
    
    
    
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('', (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))