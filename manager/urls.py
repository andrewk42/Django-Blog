from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('manager.views',
    # Index page
    url(r'^$', 'index', name='manager_home'),

    # Blog manager home
    url(r'^blog/$', 'blogHome', name='manage_blog'),

    # Blog post edit page
    url(r'blog/post/(?P<post_id>\d+)/$', 'editPost', name='edit_post'),

    # Blog comment edit page
    url(r'blog/comment/(?P<comment_id>\d+)/$', 'editComment', name='edit_comment'),

    # Blog comments by ip address edit page
    url(r'blog/(?P<url_ip_address>([\d]{1,3}_){3}[\d])/$', 'manageIP', name='manage_ip'),
)
