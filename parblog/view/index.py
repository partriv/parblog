'''
Created on Feb 30, 2012

@author: par
'''
from django import forms
from django.core.context_processors import csrf
from django.db.models.query_utils import Q
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.shortcuts import render_to_response
from parblog.models import Entry, Comment, Tag
import datetime
import calendar


from operator import itemgetter, attrgetter
from parblog import settings
from django.core.mail import send_mail

def viewbase(request, template, vars, mimetype=None):
    if request.user.is_authenticated():
        vars['user'] = request.user
    
    tagids = [t['tags'] for t in Entry.objects.get_entries().values('tags').exclude(published=None)]
    vars['tags'] = tags = Tag.objects.filter(id__in=tagids).order_by('name')
    vars['popular_entries'] = Entry.objects.get_entries().exclude(popular_index=None).order_by('popular_index')
    entrydates = Entry.objects.get_entries().values('published').order_by('-published')
    edhash = {}
    for ed in entrydates:
        ds = datetime.datetime.strftime(ed['published'], "%B %Y")
        slug = datetime.datetime.strftime(ed['published'], "/%Y/%m/")
        archhash = edhash.get(ds, {'count':0, 'date':ds, 'url':slug, 'sortobj':ed['published'].year + ed['published'].month})
        archhash['count']+=1
        edhash[ds] = archhash
    archives = edhash.values()    
    archives = sorted(archives, key=lambda x: x['sortobj'])
    archives.reverse()    
    vars['archives'] = archives
    
    vars['typekitcode'] = settings.TYPEKIT_CODE
    return render_to_response(template, vars, mimetype=mimetype)    
                                       
def index(request):
    vars = {}
    vars['entries'] = entries = Entry.objects.get_entries().order_by('-published')[:25]        
    return viewbase(request, "index.html", vars)

def archive(request, year, month):
    year, month = int(year), int(month)
    startdate = datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
    enddate = datetime.datetime(year=year, month=month, day=calendar.monthrange(year, month)[1], hour=0, minute=0, second=0)
    vars = {}
    entries = Entry.objects.get_entries().filter(published__gte=startdate, published__lte=enddate)
    vars['entries'] = entries.order_by('-published')         
    return viewbase(request, "index.html", vars)    

def tag(request, tag_slug):
    t = Tag.objects.get(name=tag_slug)
    vars = {}
    vars['tag'] = t
    vars['entries'] = entries = Entry.objects.get_entries().filter(tags=t).order_by('-published')    
    return viewbase(request, "index.html", vars)
    
def rss(request):
    vars = {}
    vars['entries'] = entries = Entry.objects.get_entries().order_by('-published')
    resp = viewbase(request, "rss.xml", vars, mimetype='text/xml')
    return resp 



class CommentForm(forms.Form):
    entry = forms.CharField(widget=forms.HiddenInput())
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=50, required=False)
    comment = forms.CharField(widget=Textarea())

    
def page(request, page_slug):    
    vars = {}    
    vars['entry'] = entry = Entry.objects.get_entries().filter(slug=page_slug)[0]
    vars.update(csrf(request))
    form = CommentForm()
    vars['comment_form'] = form     
    comments = Comment.objects.filter(entry=entry).order_by('reverse_tree_path')
    vars['comments'] = comments
                
    return viewbase(request, "page.html", vars)
    

    
def comment_post(request):
    vars = {}
    replace = request.GET.get('ctype', None)
    if request.POST:
        form = CommentForm(request.POST)
        vars['comment_form'] = CommentForm()
        if form.is_valid():
            e = Entry.objects.get(slug=form.cleaned_data.get('entry'))
            name = form.cleaned_data.get('name', None)
            comment = form.cleaned_data.get("comment", None)
            pid = form.cleaned_data.get("parent", None)
            pc = Comment.objects.get(id=pid) if pid else None
            
            subject = "New comment - %s" % e.title
            msg = "%s says: %s" % (name, comment)
            if pid:
                msg += "\n\nin reply to: %s" % pc.comment 
            send_mail(subject, msg, 'noreply@devcodehack.com', ['par.triv@gmail.com'], fail_silently=False)
            
            # REPLYING  
            c = Comment.objects.create(comment=comment, entry=e, parent=pc, name=name)                    
                            
            vars['comment'] = c
            return HttpResponse('<ul><li>' + render_to_response("comment.html", vars).content + '</li></ul>')
        else: 
            print "FORM PROBLEMS", form
            pass
            #return app_base.render(request, "app/ajax/comment_form.html", vars)    
    return HttpResponse("ES NO BUENO SENOR")
    
    
    
def goog(request):
    return HttpResponse("google-site-verification: google18fc456a29576b6a.html")

def robots(request):
    return render_to_response("robots.txt", {}, mimetype='text/plain')

def sitemap(request):
    vars = {}
    entries = Entry.objects.get_entries()
    vars['entries'] = entries
    d = datetime.datetime.now()
    vars['date'] = d.strftime('%Y-%m-%d')
    return render_to_response("sitemap.xml", vars, mimetype="text/xml")
    
