from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.forms.models import model_to_dict
from blog.models import Category, Post, Comment
from blog.forms import *
from blog.views import compileUrl
from manager.models import Settings, Visit
from manager.forms import SettingsForm, ValidSettings, formhandlerSettings
from string import capitalize, replace
from collections import OrderedDict
from copy import copy
from datetime import date

def index(request):
    return render_to_response('manager/base_manager.html')

def prepare_table_dict(sort_key, sort_dir):

    # Prepare table header values in this way so we can loop in template tags
    field_dict = OrderedDict()
    field_dict['id'] = []
    field_dict['title'] = []
    field_dict['category'] = []
    field_dict['create_date'] = []
    field_dict['publish_date'] = []
    field_dict['modified_date'] = []
    field_dict['comments'] = []
    field_dict['hits'] = []

    # Prepare values to be put in url of table headers relative to the current configuration
    for field in field_dict:
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

    return field_dict

def blogHome(request):
    # Extract GETs
    sort_key = request.GET.get('sort')
    sort_dir = request.GET.get('by')

    # For maintaining valid GETs between page loads
    get_dict = dict()
    get_dict['sort'] = sort_key
    get_dict['by'] = sort_dir

    # Process Settings form, if it was submitted
    try:
        settings_form = formhandlerSettings(request)
    except ValidSettings:
        return HttpResponseRedirect("")

    # PostForm processing
    try:
        post_form = formhandlerNewPost(request)
    except ValidNewPost as e:
        # This avoids duplicate form submissions
        return HttpResponseRedirect(reverse('edit_post', args=[e.id]))

    # General stats
    gen_dict = dict()
    gen_dict['totalcats'] = len(Category.objects.all())
    gen_dict['totalposts'] = len(Post.objects.all())
    gen_dict['totalcmts'] = len(Comment.objects.all())
    gen_dict['totalhits'] = len(Visit.objects.all())

    # Used for verifying GET values for re-ordering the Post stats table
    post_fields = [f.name for f in Post._meta.fields]
    post_fields.append('comments')
    post_fields.append('hits')
    post_fields.remove('body')

    # Verify sort_key, if it exists
    if sort_key is not None and sort_key not in post_fields:
        return HttpResponseRedirect(reverse('manage_blog'))

    # Check that sort_dir is valid
    if sort_dir is not None and sort_dir != 'asc' and sort_dir != 'desc':
        del get_dict['by']
        return HttpResponseRedirect(compileUrl('manage_blog', get_dict))

    # Always get all the posts, leave ordering to the template
    posts = Post.objects.all().order_by('-id')

    # Make a dict out of the retrieved model
    post_list = [model_to_dict(post, exclude=['body']) for post in posts]

    # Various dictionary fixups for use in templates
    for count, dic in enumerate(post_list):
        dic['category'] = posts[count].category.name
        dic['create_date'] = posts[count].create_date
        dic['modified_date'] = posts[count].modified_date
        dic['comments'] = len(posts[count].comments.all())
        dic['hits'] = len(Visit.objects.filter(path__startswith=compileUrl('blog_post_by_name', [posts[count].urlname()])))
        if dic['publish_date'] is None:
            dic['publish_date'] = date.min

    # Prepare table headers
    field_dict = prepare_table_dict(sort_key, sort_dir)

    return render_to_response('manager/blog_manager.html', {
        'post_list': post_list,
        'post_form': post_form,
        'field_data': field_dict,
        'key': sort_key,
        'dir': sort_dir,
        'settings_form': settings_form,
        'mindate': date.min,
        'gen': gen_dict,
    }, context_instance=RequestContext(request))

def editPost(request, post_id):

    # Get the referenced post, assume it is valid since this is from the manager panel
    post = Post.objects.get(id=post_id)

    # Do form processing
    try:
        form = formhandlerExistingPost(request, post)
    except PreviewPost as e:
        return render_to_response('manager/post_preview.html', {
            'post': e.post,
            'form': e.form,
        }, context_instance=RequestContext(request))
    except CloseExistingPost as e:
        return HttpResponseRedirect(reverse('edit_post', args=[post.id]))
    except ValidExistingPost:
        return HttpResponseRedirect(reverse('manage_blog'))

    # We are either showing an unedited form or one that is bound to data, with errors
    return render_to_response('manager/post_manager.html', {
        'post': post,
        'form': form,
    }, context_instance=RequestContext(request))

def editComment(request, comment_id):

    comment = Comment.objects.get(id=comment_id)

    try:
        form = formhandlerExistingComment(request, comment)
    except ValidExistingComment:
        return HttpResponseRedirect(reverse('edit_post', args=[comment.post.id]))

    return render_to_response('manager/comment_manager.html', {
        'comment': comment,
        'form': form,
    }, context_instance=RequestContext(request))

def manageIP(request, url_ip_address):
    ip_address = replace(url_ip_address, '_', '.')
    detail_request = request.GET.get('details')

    comments = Comment.objects.filter(ip_address=ip_address)
    hits = Visit.objects.filter(ip_address=ip_address).order_by('-time_stamp')

    if detail_request:
        visit_details = Visit.objects.get(id=detail_request)
    else:
        visit_details = False

    if request.method == 'POST':
        # Check for each comment's published variable in the request
        for comment in comments:
            form_data = request.POST.get(str(comment.id)+'_published')

            # If found, that comment was checked when the form was submitted
            if form_data is not None:
                comment.published = True
            else:
                comment.published = False

            comment.save()

    return render_to_response('manager/ip_manager.html', {
        'ip_address': ip_address,
        'url_ip_address': url_ip_address,
        'comments': comments,
        'hits': hits,
        'visit_details': visit_details,
    }, context_instance=RequestContext(request))
