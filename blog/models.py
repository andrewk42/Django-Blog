from django.db import models
from django.core.validators import RegexValidator, URLValidator, validate_ipv4_address, MaxLengthValidator
from blog.generators import generatePostTitle, generatePostBody, generateCommentAuthor, generateCommentBody
from string import lower, replace

# Categories for the Posts.
class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return unicode(self.name)

# Main blog posts that can only be created/manipulated by the owner.
class Post(models.Model):
    # Title generator, for testing. Not a field
    titles = generatePostTitle()

    # Automatically uses a timestamp of when the record/object is created
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="the creation timestamp")

    # Automatically uses a timestamp of when the record/object is updated/modified
    modified_date = models.DateTimeField(auto_now=True, verbose_name="the last modified timestamp")

    # This is what will be public, when the "Submit" button is pressed
    publish_date = models.DateField(null=True, blank=True, verbose_name="day this was published")

    # Titles may only have letters, numbers, spaces, underscores, or hyphens
    title = models.CharField(max_length=50, default=titles.next, help_text="Please enter a blog post title that is less than 200 characters.", validators=[RegexValidator(regex=r"^[\w -]+$", message="Enter a blog title with only letters, digits, spaces, underscores, and hyphens")])
    body = models.TextField(default=generatePostBody, help_text="Please enter a blog post body.")
    category = models.ForeignKey(Category, default=1, related_name='posts')

    class Meta:
        unique_together = ('title', 'publish_date')

    def __unicode__(self):
        return unicode(self.title)+unicode(self.create_date.strftime(" (%m-%d-%Y)"))

    def urlname(self):
        if self.publish_date is None:
            return None

        ret = lower(self.title)
        ret = replace(ret, ' ', '_')
        ret += self.publish_date.strftime("_%m-%d-%Y")
        return ret

# Comments that can be left behind by anyone.
class Comment(models.Model):
    publish_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='comments')
    author = models.CharField(max_length=30, default=generateCommentAuthor, help_text="Please enter your name.")
    homepage = models.URLField(blank=True, help_text="Please enter your homepage URL.", validators=[URLValidator])
    ip_address = models.IPAddressField(validators=[validate_ipv4_address])
    body = models.TextField(default=generateCommentBody, help_text="Please enter your comment.", validators=[MaxLengthValidator(1000)])