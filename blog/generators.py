# Stuff that makes content automatically, for testing.

import re
from random import shuffle
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
    return "A test author"

def generateCommentBody():
     with open('blog/rawtext.txt') as f:
        text = f.read()
        paragraphs = re.findall(r".+\n+", text)
        body = min(paragraphs, key=len)
        return scrambleWords(replace(body, '\n', ''))
