from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from blog.models import Post

def index(request, page_num=None):
    # This is kind of a config variable
    posts_per_page = 5

    # Calculate the amount of pages needed to show all published posts.
    # Posts will be ordered descendingly by the day they were published, and in cases where more than 1 was
    # published on the same day, will be ordered descendingly by their modified timestamp.
    all_published = Post.objects.filter(publish_date__isnull=False).order_by('-publish_date', '-modified_date')
    pub_count = len(all_published)
    page_count = pub_count / posts_per_page + bool(pub_count % posts_per_page)
    page_range = range(page_count)

    if page_num is not None:
        page_num = int(page_num)

        if page_num > page_count:
            return HttpResponseRedirect(reverse('blog_home_by_page', args=[page_count]))

        posts = all_published[(page_num-1)*5:(page_num)*5]

    else:
        # Show last 5 published posts by default
        posts = all_published[:5]

    return render_to_response('blog/base_blog.html', {
        'post_list': posts,
        'current_page': page_num,
        'last_page': page_count,
        'page_range': page_range,
    })

def getPost(request, post_id=None, post_url=None):
    if post_id is not None and post_url is None:
        return HttpResponse("Post with primary key %s." % post_id)
    elif post_id is None and post_url is not None:
        return HttpResponse("Post with urlname %s." % post_url)
    else:
        raise Http404
