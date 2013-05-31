'''
Created on Dec 30, 2010

@author: par
'''
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from parblog.managers import EntryManager



class Tag(models.Model):
    name = models.CharField(max_length=100)    


        
class Image(models.Model):
    full = models.CharField(max_length=255)
    thumb = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)

    
class Entry(models.Model):
    objects = EntryManager()
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True)
    main_image = models.ForeignKey(Image, null=True)
    total_comments = models.IntegerField(default=0)
    popular_index = models.IntegerField(null=True)


PATH_SEPARATOR = '/'
PATH_DIGITS = 10
MAX_DIGITS = 9999999999
class Comment(models.Model):
    entry = models.ForeignKey(Entry)
    comment = models.TextField()
    
    # tracking
    name = models.CharField(max_length=50, null=True)
    create_date = models.DateTimeField(auto_now_add=True)      
    modify_date = models.DateTimeField(auto_now=True) 
    
    parent = models.ForeignKey('self', related_name='parent_comment', null=True)
    last_child = models.ForeignKey('self', null=True, blank=True, related_name='lastchild_comment')
    tree_path = models.TextField(editable=False, db_index=True)
    reverse_tree_path = models.TextField(editable=False, db_index=True)

    hidden = models.BooleanField(default=False)
    
    @property
    def visible(self):
        return (self.hidden == False) == True
        
    @property
    def depth(self):
        return len(self.tree_path.split(PATH_SEPARATOR))

    @property
    def root_id(self):
        return int(self.tree_path.split(PATH_SEPARATOR)[0])
    
    @property
    def root_path(self):
        return Comment.objects.filter(pk__in=self.tree_path.
                                              split(PATH_SEPARATOR)[:-1])

    def save(self, *args, **kwargs):
        skip_tree_path = kwargs.pop('skip_tree_path', False)
        super(Comment, self).save(*args, **kwargs)
        if skip_tree_path:
            return None

        tree_path = unicode(self.pk).zfill(PATH_DIGITS)
        reverse_tree_path = str(MAX_DIGITS - self.pk)
        if self.parent:
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))
            reverse_tree_path = PATH_SEPARATOR.join((self.parent.reverse_tree_path, reverse_tree_path))

            self.parent.last_child = self
            Comment.objects.filter(pk=self.parent_id).update(last_child=self)

        self.tree_path = tree_path
        self.reverse_tree_path = reverse_tree_path
        Comment.objects.filter(pk=self.pk).update(tree_path=self.tree_path, reverse_tree_path=reverse_tree_path)

@receiver(pre_save, sender=Comment)
def pre_save_comment(sender, **kwargs):    
    comment = kwargs.get('instance', None)
    entry = Entry.objects.get(id=comment.entry.id)
    if comment.hidden:
        entry.total_comments -= 1
    else:
        entry.total_comments += 1
    entry.save()
        
    #class Meta(object):
    #    ordering = ('tree_path',)