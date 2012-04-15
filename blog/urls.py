from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('blog.views',
    # Index page
    url(r'^$', 'index', name='blog_home'),

    # Index with page number
    url(r'^page/(?P<page_num>\d+)/$', 'index', name='blog_home_by_page'),

    # Specific post primary key reference
    url(r'^(?P<post_id>\d+)/$', 'getPost', name='blog_post_by_id'),

    # Specific post readable name (urlname) reference
    url(r'^(?P<post_url>[\w -]+)/$', 'getPost', name='blog_post_by_name'),
)
