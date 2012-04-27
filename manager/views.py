from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from blog.models import Post, PostForm
from blog.views import compileUrl
from string import capitalize
from collections import OrderedDict
from datetime import date

def index(request):
    return render_to_response('manager/base_manager.html')

def blogHome(request):
    # Extract GETs
    sort_key = request.GET.get('sort')
    sort_dir = request.GET.get('by')

    # For maintaining valid GETs between page loads
    get_dict = dict()
    get_dict['sort'] = sort_key
    get_dict['by'] = sort_dir

    # Used for verifying GET values for re-ordering the Post stats table
    post_fields = [f.name for f in Post._meta.fields]
    post_fields.append('comments')
    post_fields.remove('body')

    # Verify sort_key, if it exists
    if sort_key is not None and sort_key not in post_fields:
        return HttpResponseRedirect(reverse('manage_blog'))

    # Check for sort_dir, and if invalid refresh the page with the valid sort_key
    if sort_dir == 'asc':
        sort_char = ''
    elif sort_dir is None or sort_dir == 'desc':
        sort_char = '-'
    else:
        del get_dict['by']
        return HttpResponseRedirect(compileUrl('manage_blog', get_dict))

    # Always get all the posts, but order them depending on the state of the GET variables
    if sort_key is None:
        posts = Post.objects.all().order_by('-id')
    elif sort_key == 'comments':
        # Special case since 'comments' is a related field and not an actual field
        posts = Post.objects.all().annotate(cmt_count=Count('comments')).order_by(sort_char+'cmt_count')
    else:
        posts = Post.objects.all().order_by(sort_char+sort_key)

    # Form processing
    if request.method == 'POST':
        # Create a form/new model entry from POST data
        form = PostForm(request.POST)

        if form.is_valid():
            m = form.save()

            # This avoids duplicate form submissions
            return HttpResponseRedirect(reverse('edit_post', args=[m.id]))

    # New, unbound form case
    else:
        # Override the default values in the model, which are really meant for testing
        blank_post = Post(title="", body="")
        form = PostForm(instance=blank_post)

    # Prepare table header values in this way to simplify template tags
    field_dict = OrderedDict()
    field_dict['id'] = []
    field_dict['title'] = []
    field_dict['category'] = []
    field_dict['create_date'] = []
    field_dict['publish_date'] = []
    field_dict['modified_date'] = []
    field_dict['comments'] = []

    # More overcomplicated table ordering logic
    for field in post_fields:
        if field == 'create_date':
            name = "Date Created"
        elif field == 'modified_date':
            name = "Date Last Modified"
        elif field == 'publish_date':
            name = "Date Published"
        else:
            name = capitalize(field)

        if field == sort_key:
            if sort_dir == 'asc':
                field_dict[field] = ['desc', name]
            else:
                field_dict[field] = ['asc', name]
        elif field == 'id' and sort_key is None:
            field_dict[field] = ['asc', name]
        else:
            field_dict[field] = ['desc', name]

    return render_to_response('manager/blog_manager.html', {
        'post_list': posts,
        'form': form,
        'field_data': field_dict,
        'key': sort_key,
    }, context_instance=RequestContext(request))

def handlePostForm(request, form):
    recognized_keys = ['preview', 'save', 'publish']

    # Assume first recognized key (there should only be 1 at a time)
    for key in recognized_keys:
        if key in request.POST:
            break
    # If none recnognized, how did we get here?
    else:
        raise Http404

    # If we're previewing, don't save anything but show the submitted data in the preview template
    if key == 'preview':
        # Make a temporary version of the post
        post = form.save(commit=False)

        return render_to_response('manager/post_preview.html', {
            'post': post,
            'form': form,
        }, context_instance=RequestContext(request))

    # If we're just saving, save the valid data and reload the page with an unbound form
    elif key == 'save':
        form.save()
        return HttpResponseRedirect(reverse('manage_blog'))

    # Otherwise we're publishing
    else:
        post = form.save(commit=False)

        if post.publish_date is None:
            post.publish_date = date.today()
            post.save()

        return HttpResponseRedirect(reverse('manage_blog'))

def editPost(request, post_id):

    # Get the referenced post, assume it is valid since this is from the manager panel
    post = Post.objects.get(id=post_id)

    # Check if we got here by submitting the form
    if request.method == 'POST':
        # Create a form/existing model entry from a model ref, and POST data
        form = PostForm(request.POST, instance=post)

        # If the form is valid, decide which page this is from/appropriate action
        if form.is_valid():
            return handlePostForm(request, form)

        # If form isn't valid, fall through

    # If here, we just came to the edit page without the form
    else:
        form = PostForm(instance=post)

    # We are either showing an unedited form or one that is bound to data, with errors
    return render_to_response('manager/post_manager.html', {
        'post': post,
        'form': form,
    }, context_instance=RequestContext(request))
