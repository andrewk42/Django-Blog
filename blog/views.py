from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from blog.models import Post, Category

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
    posts_per_page = 3

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

    return render_to_response('blog/base_blog.html', {
        'post_list': posts,
        'current_page': page_num,
        'filter_name': filter_name,
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
