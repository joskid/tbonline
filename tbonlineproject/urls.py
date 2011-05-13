from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin

from contact_form.views import contact_form

from post.views import PublishedFrontPagePostsView

from post.forms import EnhancedContactForm

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', PublishedFrontPagePostsView.as_view(template_name = 'index.html'), 
        name='home'),
    (r'^posts/', include('post.urls')),
    (r'^galleries/', include('gallery.urls')),
    (r'^stories/', include('story.urls')),
    (r'^feeders/', include('feeder.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^search/', include('haystack.urls')),
    url(r'^contact/$', contact_form, {'form_class': EnhancedContactForm}, name='contact'),                            
    (r'^contact/', include('contact_form.urls')),
    (r'^enhancedtext/', include('enhancedtext.urls')),    
    (r'^grappelli/', include('grappelli.urls')),
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    


    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

