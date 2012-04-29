from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from blog.models import Post, Category, Comment
from blog.forms import CommentForm, formhandlerNewComment
from string import replace
import re

def compileUrl(urlname, get_dict=None):
    # First make sure the urlname is valid and set it to a return value
    ret = reverse(urlname)

    # Check if we have any GET variables to append to the return value
    if get_dict and len(get_dict) > 0:
        ret += '?'

        for name, value in get_dict.items():
            ret += str(name)+'='+str(value)+'&'
        else:
            # Chop off the trailing '&' after the last iteration
            ret = ret[:-1]

    return ret

def index(request):
    # This is kind of a config variable
    posts_per_page = 4

    # Extract GETs
    page_num = request.GET.get('page')
    filter_name = request.GET.get('filter')

    get_dict = dict()
    get_dict['filter'] = filter_name
    get_dict['page'] = page_num

    # Filter by category logic. Shortens the master list
    if filter_name is not None:
        try:
            category = Category.objects.get(name=filter_name)

            # If a valid category was provided, only get posts from this category
            master_list = Post.objects.filter(category=category, publish_date__isnull=False).order_by('-publish_date', '-modified_date')

        except Category.DoesNotExist:
            # If a valid category wasn't provided, refresh the page without the filter, but preserve page
            del get_dict['filter']
            return HttpResponseRedirect(compileUrl('blog_home', get_dict))

    else:
        master_list = Post.objects.filter(publish_date__isnull=False).order_by('-publish_date', '-modified_date')

    # Calculate the amount of pages needed to show all published posts.
    # Posts will be ordered descendingly by the day they were published, and in cases where more than 1 was
    # published on the same day, will be ordered descendingly by their modified timestamp.
    pub_count = len(master_list)
    page_count = pub_count / posts_per_page + bool(pub_count % posts_per_page)
    page_range = range(page_count)

    if page_num is not None:
        page_num = int(page_num)

        if page_num > page_count:
            get_dict['page'] = page_count
            return HttpResponseRedirect(compileUrl('blog_home', get_dict))
        elif page_num < 1:
            get_dict['page'] = 1
            return HttpResponseRedirect(compileUrl('blog_home', get_dict))

        posts = master_list[(page_num-1)*posts_per_page:(page_num)*posts_per_page]

    else:
        # Show first page by default
        posts = master_list[:posts_per_page]

    data = []

    # Assemble the posts/comments in a weird way so that both lists can be iterated over in one template for loop
    for post in posts:
        data.append([post, Comment.objects.filter(post=post, published=True)])

    return render_to_response('blog/base_blog.html', {
        'post_list': data,
        'current_page': page_num,
        'filter_name': filter_name,
        'last_page': page_count,
        'page_range': page_range,
    })

def postDetail(request, post_url):
    match = re.match(r'^([\w-]+)_([\d]{2})-([\d]{2})-([\d]{4})$', post_url)

    if match is None:
        raise Http404

    post_title = replace(match.group(1), '_', ' ')
    post_pub_date = match.group(4)+'-'+match.group(2)+'-'+match.group(3)

    post = Post.objects.get(publish_date=post_pub_date, title=post_title)
    comments = Comment.objects.filter(post=post, published=True)

    form = formhandlerNewComment(request, post)

    if form.is_valid():
        # This avoids duplicate form submissions
        return HttpResponseRedirect("")

    # Create a form/existing model entry from a model ref
    # i.e. for a published comment that is to be edited
    # form = CommentForm(instance=Comment.objects.get)

    # Create a form/existing model entry from a model ref, and POST data
    # i.e. for a published comment that is being edited but is bound to data
    # form = CommentForm(request.POST, instance=Comment.objects.get)

    return render_to_response('blog/post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments,
    }, context_instance=RequestContext(request))
