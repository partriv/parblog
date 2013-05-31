'''
Created on Dec 8, 2011

@author: eneve
'''

def pretty_date_time(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago" if second_diff != 1 else str(day_diff/30) + " second ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago" if second_diff/60 != 1 else str(day_diff/30) + " minute ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago" if second_diff/3600 != 1 else str(day_diff/30) + " hour ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago" if day_diff != 1 else str(day_diff/7) + " day ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago" if day_diff/7 != 1 else str(day_diff/7) + " week ago" 
    if day_diff < 365:
        return str(day_diff/30) + " months ago" if day_diff/30 != 1 else str(day_diff/30) + " month ago"
    return str(day_diff/365) + " years ago" if day_diff/365 != 1 else str(day_diff/365) + " year ago"