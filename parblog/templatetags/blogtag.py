'''
Created on Mar 2, 2012

@author: par
'''

from parblog.util.comment_util import annotate_tree_properties, fill_tree
from parblog.util.datetime_util import pretty_date_time
from django import template

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

register = template.Library()

CONTENT_LEN = 650


def clean_content(content): return strip_tags(content)
register.filter(clean_content)

def clean_snippet(content): return strip_tags(content)[:250]
register.filter(clean_snippet)

def too_long(content): return len(content) > CONTENT_LEN
register.filter(too_long)

def replaceWithContents(element):
    ix= element.parent.contents.index(element)
    for child in reversed(element.contents):
        element.parent.insert(ix, child)
    element.extract()

def snippet(content): 
    if len(content) > CONTENT_LEN:
        
        doc = BeautifulSoup(content) # maybe fromEncoding= 'utf-8'
        for link in doc.findAll('a'):
            replaceWithContents(link)
        doc = str(doc)
        
        return doc[:CONTENT_LEN]
    else: 
        return content
register.filter(snippet)

def annotate_tree(comments): return annotate_tree_properties(comments)
register.filter(annotate_tree)

def how_long_ago(time): return pretty_date_time(time)
register.filter(how_long_ago)

register.filter(fill_tree)
