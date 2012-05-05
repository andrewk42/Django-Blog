from django.http import Http404
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

class ValidNewPost(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "The processed Post form is valid and has been saved with primary key "+str(self.id)

class ValidExistingPost(Exception):
    def __str__(self):
        return "The processed PostForm is valid"

class PreviewPost(Exception):
    def __init__(self, post, form):
        self.post = post
        self.form = form

    def __str__(self):
        return "The processed PostForm is valid and being previewed"

class CloseExistingPost(ValidNewPost):
    def __str__(self):
        return "The processed Post is valid, is being closed, and has been saved with primary key"+str(self.id)

class ValidNewComment(ValidExistingPost):
    def __str__(self):
        return "The processed CommentForm is valid)"

class ValidExistingComment(ValidExistingPost):
    def __str__(self):
        return "The processed CommentForm is valid"

def formhandlerNewPost(request):
    if request.method == 'POST':
        # Create a form/new model entry from POST data
        post_form = PostForm(request.POST)

        if post_form.is_valid():
            m = post_form.save()

            # This avoids duplicate form submissions
            raise ValidNewPost(m.id)

    # New, unbound form case
    else:
        # Override the default values in the model, which are really meant for testing
        blank_post = Post(title="", body="")
        post_form = PostForm(instance=blank_post)

    return post_form

def formhandlerExistingPost(request, post):
    recognized_keys = ['preview', 'save', 'publish', 'close']

    # Check if we got here by submitting the form
    if request.method == 'POST':
        # Create a form/existing model entry from a model ref, and POST data
        form = PostForm(request.POST, instance=post)

        # If the form is valid, decide which page this is from/appropriate action
        if form.is_valid():
            # Assume first recognized key (there should only be 1 at a time)
            for key in recognized_keys:
                if key in request.POST:
                    break
            # If none recognized, how did we get here?
            else:
                raise Http404

            # If we're previewing, don't save anything but show the submitted data in the preview template
            if key == 'preview':
                # Make a temporary version of the post
                post = form.save(commit=False)

                raise PreviewPost(post, form)

            # If we're just saving, save the valid data and reload the page with an unbound form
            elif key == 'save':
                form.save()
                raise ValidExistingPost()

            # Close/unpublish a post
            elif key == 'close':
                post = form.save(commit=False)
                post.publish_date = None
                post.save()
                raise CloseExistingPost(post.id)

            # Otherwise we're publishing
            else:
                post = form.save(commit=False)

                if post.publish_date is None:
                    post.publish_date = date.today()
                    post.save()

                raise ValidExistingPost

        # If form isn't valid, fall through

    # If here, we just came to the edit page without the form
    else:
        form = PostForm(instance=post)

    return form

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
            raise ValidNewComment

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
            raise ValidExistingComment

    # New, unbound form case
    else:
        form = CommentForm(instance=comment)

    return form
