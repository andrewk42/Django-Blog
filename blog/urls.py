from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('blog.views',
    # Index page
    url(r'^$', 'index'),

    # Specific post primary key reference
    url(r'^(?P<post_id>\d+)/$', 'getPost'),

    # Specific post readable name (urlname) reference
    url(r'^(?P<post_url>[\w -]+)/$', 'getPost'),
)
