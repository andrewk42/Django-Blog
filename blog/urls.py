from django.conf.urls.defaults import patterns, url
from blog.models import Category

urlpatterns = patterns('blog.views',
    # Index page
    url(r'^$', 'index', name='blog_home'),

    # Specific post primary key reference
    url(r'^(?P<post_id>\d+)/$', 'getPost', name='blog_post_by_id'),

    # Specific post readable name (urlname) reference
    url(r'^(?P<post_url>[\w -]+)/$', 'getPost', name='blog_post_by_name'),
)
