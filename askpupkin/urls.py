from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ask.views',
    # Examples:
    url(r'^$', 'index_latest', name='index_latest'),
    url(r'^new/$', 'index_latest', name='index_latest'),
    url(r'^popular/$', 'index_popular', name='index_popular'),
    url(r'^question/$', 'question', name='question'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
