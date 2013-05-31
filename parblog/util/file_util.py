'''
Created on Feb 20, 2011

@author: par
'''
from parblog import settings_local
import os
from PIL import Image


def uploadFile(thefile):
    medroot = settings_local.MEDIA_ROOT if settings_local.MEDIA_ROOT.endswith('/') else settings_local.MEDIA_ROOT + '/'
    uploadPath = medroot + 'ugc/'
    uploadPath = uploadPath + thefile.name
    ext = uploadPath[uploadPath.rfind('.'):]
    thumbPath = uploadPath.replace(ext, '-thumb' + ext)
    
    
    # write file
    destination = open(uploadPath, 'wb+')
    for chunk in thefile.chunks():
        destination.write(chunk)
    destination.close()

    # create thumbnails
    img = Image.open(uploadPath)
    img.thumbnail((250, 250), Image.ANTIALIAS)
    img.save(thumbPath)

    
    
    return os.path.split(uploadPath)[1], os.path.split(thumbPath)[1]