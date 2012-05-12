from django.db import models
from django.core.validators import RegexValidator, URLValidator, validate_ipv4_address, MaxLengthValidator
from blog.generators import generatePostTitle, generatePostBody, generateCommentAuthor, generateCommentBody
from string import lower, replace

# Categories for the Posts.
class Category(models.Model):
    name = models.CharField(max_length=30, unique=True, validators=[RegexValidator(regex=r"^[A-Za-z ]+$", message="Enter a category with only letters or spaces")])

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return unicode(self.name)

# Main blog posts that can only be created/manipulated by the owner.
class PostAbstract(models.Model):
    # Title generator, for testing. Not a field
    titles = generatePostTitle()

    # Automatically uses a timestamp of when the record/object is created
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="the creation timestamp")

    # Automatically uses a timestamp of when the record/object is updated/modified
    modified_date = models.DateTimeField(auto_now=True, verbose_name="the last modified timestamp")

    # This is what will be public, when the "Submit" button is pressed
    publish_date = models.DateField(null=True, blank=True, verbose_name="day this was published")

    # Titles may only have letters, numbers, spaces, underscores, or hyphens
    title = models.CharField(max_length=50, default=titles.next, help_text="Please enter a blog post title that is less than 50 characters.", validators=[RegexValidator(regex=r"^[A-Za-z0-9 -]+$", message="Enter a blog title with only letters, digits, spaces, and hyphens")])
    body = models.TextField(default=generatePostBody, help_text="Please enter a blog post body.")
    category = models.ForeignKey(Category, default=1, related_name='%(class)s_posts')

    class Meta:
        abstract = True

    def urlname(self):
        if self.publish_date is None:
            return None

        ret = lower(self.title)
        ret = replace(ret, ' ', '_')
        ret += self.publish_date.strftime("_%m-%d-%Y")
        return ret

class Post(PostAbstract):
    class Meta:
        unique_together = ('title', 'publish_date')

    def save(self, revision=True, *args, **kwargs):
        if revision:
            try:
                # Check if this object already existed before
                p = Post.objects.get(id=self.id)

                # Check if the title, body, or category fields are different
                if self.title != p.title or self.body != p.body or self.category != p.category:
                    r = PostRevision()

                    for field in self._meta.fields:
                        if field.name != 'id':
                            exec('r.'+field.name+'=p.'+field.name)

                    r.post = p
                    r.save()

            except Post.DoesNotExist:
                # If this is the first instance of this Post just save normally
                pass

        super(Post, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.title)+unicode(self.create_date.strftime(" (%m-%d-%Y)"))

class PostRevision(PostAbstract):
    post = models.ForeignKey(Post, related_name='post_revisions')

    def save(self, *args, **kwargs):
        super(PostRevision, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Revision "+unicode(self.id)+" for "+unicode(self.title)+unicode(self.create_date.strftime(" (%m-%d-%Y)"))

# Comments that can be left behind by anyone.
class CommentAbstract(models.Model):
    publish_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, default=1, related_name='%(class)s_comments')
    author = models.CharField(max_length=30, default=generateCommentAuthor, help_text="Please enter your name.")
    homepage = models.URLField(blank=True, help_text="Please enter your homepage URL.", validators=[URLValidator])
    ip_address = models.IPAddressField(default="127.0.0.1", validators=[validate_ipv4_address])
    published = models.BooleanField(default=True, help_text="Comments not published can only be seen from the admin/manager pages")
    # Not a field, just for easy reference by both validator and form
    body_max = 3000
    body = models.TextField(default=generateCommentBody, help_text="Please enter your comment.", validators=[MaxLengthValidator(body_max)])

    class Meta:
        abstract = True

    def ipUrlname(self):
        ret = replace(str(self.ip_address), '.', '_')
        return ret

class Comment(CommentAbstract):
    def save(self, revision=True, *args, **kwargs):
        if revision:
            try:
                # Check if this object already existed before
                c = Comment.objects.get(id=self.id)

                # Check if the title, body, or category fields are different
                if self.author != c.author or self.homepage != c.homepage or self.body != c.body:
                    r = CommentRevision()

                    for field in self._meta.fields:
                        if field.name != 'id':
                            exec('r.'+field.name+'=c.'+field.name)

                    r.comment = c
                    r.save()

            except Comment.DoesNotExist:
                # If this is the first instance of this Comment just save normally
                pass

        super(Comment, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Comment by "+unicode(self.author)+unicode(self.publish_date.strftime(" (%m-%d-%Y_%H-%M-%S)"))

class CommentRevision(CommentAbstract):
    comment = models.ForeignKey(Comment, related_name='comment_revisions')

    # Don't want recursive behaviour so override Comment's custom save
    def save(self, *args, **kwargs):
        super(CommentRevision, self).save(*args, **kwargs)
