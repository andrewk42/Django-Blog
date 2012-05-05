from django.conf.urls.defaults import patterns, url
from django.core.signals import request_started

urlpatterns = patterns('blog.views',
    # Index page
    url(r'^$', 'index', name='blog_home'),

    # Specific post readable name (urlname) reference
    url(r'^(?P<post_url>[\w-]+)/$', 'postDetail', name='blog_post_by_name'),
)
