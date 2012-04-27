from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('manager.views',
    # Index page
    url(r'^$', 'index', name='manager_home'),

    # Blog manager home
    url(r'^blog/$', 'blogHome', name='manage_blog'),

    # Blog post edit page
    url(r'blog/post/(?P<post_id>\d+)/$', 'editPost', name='edit_post'),
)
