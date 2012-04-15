# Stuff that makes content automatically, for testing.

import re
from random import shuffle, randrange, random
from string import replace

def scrambleWords(paragraph):
    l = paragraph.split(' ')
    shuffle(l)
    return ' '.join(l)

def generatePostTitle():
    count = 0

    while True:
        command = yield "Test post "+str(count)

        if command == "reset":
            count = 0
        else:
            count += 1

def generatePostBody():
    with open('blog/rawtext.txt') as f:
        text = f.read()
        paragraphs = re.findall(r".+\n+", text)
        body = max(paragraphs, key=len)
        return scrambleWords(replace(body, '\n', ''))

def generateCommentAuthor():
    count = 0

    while True:
        command = yield "A test author "+str(count)

        if command == "reset":
            count = 0
        else:
            count += 1

def generateCommentBody():
     with open('blog/rawtext.txt') as f:
        text = f.read()
        paragraphs = re.findall(r".+\n+", text)
        body = min(paragraphs, key=len)
        return scrambleWords(replace(body, '\n', ''))


#
# The following functions are extra sloppy and are meant to be called from the
# manage.py shell
#

def generateCategories():
    from djangoroot.blog.models import Category, Post, Comment

    c = Category(name="Programming")
    c.save()
    c = Category(name="Music")
    c.save()
    c = Category(name="Gaming")
    c.save()
    c = Category(name="School")
    c.save()

def generatePosts(amount=10):
    from djangoroot.blog.models import Category, Post, Comment
    from datetime import date
    from time import sleep

    category_range = len(Category.objects.all())

    if category_range == 0:
        print "Error: No categories!"
        return

    for i in range(amount):
        c = Category.objects.get(id=randrange(1, category_range+1))
        p = Post(category=c)

        if random() > .2:
            p.publish_date = date.today()

        p.save()
        sleep(2)
        

def generateComments(amount=10, post_id=None):
    from djangoroot.blog.models import Category, Post, Comment
    from time import sleep

    if post_id is None:
        post_range = len(Post.objects.all())

        if post_range == 0:
            print "Error: No posts!"
            return

    else:
        try:
            p = Post.objects.get(id=post_id)
        except:
            print "Error: Invalid post id!"
            return

    for i in range(amount):
        if post_id is None:
            p = Post.objects.get(id=randrange(1, post_range+1))

        c = Comment(post=p)
        c.save()
        sleep(2)
