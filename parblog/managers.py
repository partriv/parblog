'''
Created on Mar 4, 2012

@author: par
'''
from django.db import models
import datetime


class EntryManager(models.Manager):
    def get_entries(self):
        return self.filter(deleted=False, published__lt=datetime.datetime.now()).exclude(published=None)