'''
Created on Mar 1, 2012

@author: par
'''
from django import forms
from django.forms.widgets import PasswordInput, Textarea
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms.models import ModelForm, ModelChoiceField
from parblog.models import Entry, Tag, Image
import datetime
from django.template.defaultfilters import slugify
from parblog.util import file_util


@login_required
def preview(request, page_slug):    
    vars = {}    
    vars['entry'] = entry = Entry.objects.get(slug=page_slug)    
    
                
    return render_to_response("page.html", vars)
    

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full

IMAGES = [(i.id, i.full) for i in Image.objects.all().order_by('-created')]
class EntryForm(forms.Form):
    title = forms.CharField(max_length=100)
    slug = forms.CharField(max_length=100, help_text='You cant change this.', required=False)
    content = forms.CharField(widget=Textarea(), required=False)
    tags = forms.CharField(max_length=400, required=False)
    published = forms.DateTimeField(required=False)
    main_image = MyModelChoiceField(queryset=Image.objects.all().order_by('-created'), required=False)
    popular_index = forms.IntegerField(required=False)


def adminbase(request, template, vars):
    vars['user'] = request.user
    return render_to_response(template, vars)

@login_required
def index(request):
    vars = {}    
    vars['entries'] = Entry.objects.all().order_by('-created')
    return adminbase(request, "admin/admin.html", vars)

        
@login_required
def entry(request):
    vars = {}
    vars.update(csrf(request))
    eid, eid_entry = request.GET.get('eid', None), None
    if eid: vars['eid_entry'] = eid_entry = Entry.objects.get(id=eid)    
    if request.POST:
        form = EntryForm(request.POST)
        if form.is_valid(): 
            title = form.cleaned_data.get('title')           
            if eid_entry:
                en = eid_entry
            else:
                en = Entry()
                en.total_comments = 0
                 
            en.title = title
            en.popular_index = form.cleaned_data.get('popular_index')
            
            if en.published == None:
                slug = slugify(title)
                ecnt = Entry.objects.filter(slug__startswith=slug).exclude(published=None).count()
                if ecnt > 0: slug = '%s-%d' % (slug, ecnt)
                en.slug = slug
            else:
                en.slug = form.cleaned_data.get('slug')
            
            en.content = form.cleaned_data.get('content')
            en.author = request.user
            en.published = form.cleaned_data.get('published', None)
            en.main_image = form.cleaned_data.get("main_image", None)
             
            en.save()
            en.tags.all().delete()
            for tagstr in form.cleaned_data.get('tags', '').split(','):
                ts = tagstr.strip()
                if ts:
                    t, created = Tag.objects.get_or_create(name=ts)
                    en.tags.add(t)
            en.save()
            return HttpResponseRedirect("/admin/entry/?eid=%d" % en.id)
                
    iv = {}
    if eid_entry:
        e = eid_entry
        iv['title'] = e.title
        iv['slug'] = e.slug
        iv['content'] = e.content
        iv['published'] = e.published
        tagstr = ''
        for t in e.tags.all():
            tagstr += t.name + ', '
        iv['tags'] = tagstr.strip(' ').strip(',')
        iv['main_image'] = e.main_image.id if e.main_image else ''
        iv['popular_index'] = e.popular_index
    form = EntryForm(initial=iv)        
    vars['form'] = form
    return adminbase(request, "admin/entry.html", vars)


#----------------------------------------------------------------------------
#--------------------------- IMAGES -----------------------------------------
class UploadFileForm(forms.Form):    
    file  = forms.FileField()

@login_required
def images(request):
    vars = {}
    
    vars = {}
    vars.update(csrf(request))
    vars['form'] = UploadFileForm()
    

    vars['images'] = Image.objects.all().order_by('-created')
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fullpath, thumbpath = file_util.uploadFile(request.FILES['file'])
            print fullpath, thumbpath
            i, created = Image.objects.get_or_create(full=fullpath)
            i.thumb = thumbpath
            i.save()            
            return HttpResponseRedirect('/admin/images/')
                
    
    return adminbase(request, "admin/imageadd.html", vars)
    




#----------------------------------------------------------------------------
#-------------------------------------- LOGIN -------------------------------

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=PasswordInput())
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        un = cleaned_data.get("username")
        pw = cleaned_data.get("password")
        print un, pw
        if un and pw:
            user = auth.authenticate(username=un, password=pw)
            if user and user.is_active: return cleaned_data
            
        raise forms.ValidationError("Invalid Login.")

def login(request):
    vars = {}
    form = LoginForm()
    vars.update(csrf(request))
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            auth.login(request, user)
            return HttpResponseRedirect('/admin/') # Redirect after POST
    
    vars['form'] = form
    return render_to_response("admin/login.html", vars)            

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/") 