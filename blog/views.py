from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from blog.models import Post

def index(request):
    posts = Post.objects.filter(publish_date__isnull=False).order_by('-publish_date')[:5]

    return render_to_response('blog/base_blog.html', {
        'post_list': posts
    })

def getPost(request, post_id=None, post_url=None):
    if post_id is not None and post_url is None:
        return HttpResponse("Post with primary key %s." % post_id)
    elif post_id is None and post_url is not None:
        return HttpResponse("Post with urlname %s." % post_url)
    else:
        raise Http404
        #return HttpResponse("What the hell happened. ID: %s url: %s" % post_id, post_url)
