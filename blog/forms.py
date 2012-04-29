from django.http import HttpResponseRedirect, Http404
from django.forms import ModelForm, TextInput, Textarea
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from blog.models import Post, Comment
from datetime import date

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('category', 'title', 'body')

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('publish_date', 'post', 'ip_address')
        # These are included with several default attributes
        widgets = {
            'author': TextInput(attrs={'autocomplete': 'on'}),
            'homepage': TextInput(attrs={'type': 'url', 'autocomplete': 'on'}), # There is a bug where 'type'='url' doesn't work
            'body': Textarea(attrs={'maxlength': model.body_max, 'required': 'required'})
        }

def formhandlerPost(request, form):
    recognized_keys = ['preview', 'save', 'publish', 'close']

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

    # Close/unpublish a post
    elif key == 'close':
        post = form.save(commit=False)
        post.publish_date = None
        post.save()

        return HttpResponseRedirect(reverse('edit_post', args=[post.id]))

    # Otherwise we're publishing
    else:
        post = form.save(commit=False)

        if post.publish_date is None:
            post.publish_date = date.today()
            post.save()

        return HttpResponseRedirect(reverse('manage_blog'))

def formhandlerNewComment(request, post):
    # If the form has been submitted
    if request.method == 'POST':
        # Create a form/new model entry from POST data
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = request.META['REMOTE_ADDR']
            comment.save()

    # New, unbound form case
    else:
        # Override the default values in the model, which are really meant for testing
        blank_comment = Comment(author='', body='')
        form = CommentForm(instance=blank_comment)

    return form

def formhandlerExistingComment(request, comment):
    # If the form has been submitted
    if request.method == 'POST':
        # Get an existing form/model and populate with POST
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()

    # New, unbound form case
    else:
        form = CommentForm(instance=comment)

    return form
