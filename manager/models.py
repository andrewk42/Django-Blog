from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, validate_ipv4_address, URLValidator
from datetime import datetime, timedelta
#from threading import Thread

last_hit_timestamp = datetime.now()

class Settings(models.Model):
    blog_posts_per_page = models.IntegerField(default=3, help_text="The number of posts shown on the main page", validators=[MaxValueValidator(10), MinValueValidator(2)])

    class Meta:
        verbose_name_plural = "Settings"

    # Ensure that we never save more than 1 row in this table
    def save(self, *args, **kwargs):
        self.id = 1
        super(Settings, self).save(*args, **kwargs)

    # Ensure that we never delete the only row in this table
    def delete(self):
        pass

    def __unicode__(self):
        return "Posts per page: "+unicode(self.posts_per_page)

class Visit(models.Model):
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="the time this visit occurred at")
    ip_address = models.IPAddressField(editable=False, validators=[validate_ipv4_address])
    path = models.URLField(editable=False, validators=[URLValidator])
    referrer = models.URLField(null=True, editable=False, validators=[URLValidator])
    user_agent = models.CharField(max_length=400, editable=False)
    full_header = models.TextField(editable=False, verbose_name="the entire HTTP request header")
    full_body = models.TextField(editable=False, verbose_name="the entire HTTP request body")

    class Meta:
        unique_together = ('time_stamp', 'ip_address')

    def __unicode__(self):
        return unicode(self.ip_address)+" | "+unicode(self.time_stamp)

class VisitMiddleware(object):
    """
    Middleware that handles HTTP request logging.
    """

    def process_request(self, request):
        # Don't log duplicate requests
        if '.ico' in request.path or '.css' in request.path:
            return

        try:
            v = Visit()
            v.ip_address = request.META.get('REMOTE_ADDR')
            v.path = request.get_full_path()
            v.referrer = request.META.get('HTTP_REFERER')
            v.user_agent = request.META.get('HTTP_USER_AGENT')
            v.full_header = '\n'.join([str(key)+": "+str(value) for key, value in request.META.items()])
            v.full_body = request.raw_post_data
            v.save()
        except:
            pass
