from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.home', name='home'),

    url(r'^changeset_added/$', 'main.views.changeset_added', 
        name='changeset_added'),

    url(r'^checkout/$', 'main.views.checkout_index', name='checkout_index'),
    url(r'^templateset/$', 'main.views.templatesets_index', name='templatesets_index'),

    url(r'^checkout/(?P<slug>[\w\d_\-]+)/$', 'main.views.checkout_overview',
        name='checkout_overview'),
    url(r'^checkout/(?P<slug>[\w\d_\-]+)/checkin/$', 'main.views.templateset_checkin',
        name='templateset_checkin'),

    url(r'^codeblock/create/$', 'main.views.codeblock_create',
        name='codeblock_create'),
    url(r'^codeblock/edit/(?P<filename>[\w\d_\-\./]+)/$', 'main.views.codeblock_edit',
        name='codeblock_edit'),
    url(r'^codeblock/diff/(?P<filename>[\w\d_\-\./]+)/$', 
        'main.views.codeblock_diff',
        name='codeblock_diff'),

    url(r'^templateset/(?P<id>\d+)/$', 'main.views.templateset_overview',
        name='templateset_overview'),
    url(r'^templateset/(?P<id>\d+)/checkout/$', 'main.views.templateset_checkout',
        name='templateset_checkout'),

    url(r'^templateset/(?P<id>\d+)/(?P<filename>[\w\d_\-\.]+)/$', 'main.views.templateset_template',
        name='templateset_template'),
    url(r'^templateset/(?P<id>\d+)/(?P<filename>[\w\d_\-\.]+)/(?P<hash1>[a-f0-9]+)/(?P<hash2>[a-f0-9]+)/$',
        'main.views.templateset_templatediff',
        name='templateset_templatediff'),
    
    url(r'^templateset/(?P<id>\d+)/(?P<filename>[\w\d_\-\.]+)/edit/$', 
        'main.views.templateset_template_edit',
        name='templateset_template_edit'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    (r'^accounts/login/$', 'login'),
    (r'^accounts/logout/$', 'logout'),
)
