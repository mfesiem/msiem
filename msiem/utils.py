
# -*- coding: utf-8 -*-
"""
    msiem utils
"""

import time
import base64
import re
from functools import wraps
import logging
from .constants import POSSIBLE_TIME_RANGE
from .exceptions import ESMException
from datetime import datetime, timedelta

logging.getLogger("urllib3").setLevel(logging.WARNING)

def getLogger(v=False, logfile=None):

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    std = logging.StreamHandler()
    std.setLevel(logging.DEBUG)
    std.setFormatter(formatter)

    if v :
        std.setLevel(logging.DEBUG)
    else :
        std.setLevel(logging.INFO)
        
    log.addHandler(std)

    if logfile :
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        log.addHandler(fh)

    return (log)

def dehexify(data):
    """
    A URL and Hexadecimal Decoding Library.

    Credit: Larry Dewey
    """

    hexen = {
        '\x1c': ',',  # Replacing Device Control 1 with a comma.
        '\x11': '\n',  # Replacing Device Control 2 with a new line.
        '\x12': ' ',  # Space
        '\x22': '"',  # Double Quotes
        '\x23': '#',  # Number Symbol
        '\x27': '\'',  # Single Quote
        '\x28': '(',  # Open Parenthesis
        '\x29': ')',  # Close Parenthesis
        '\x2b': '+',  # Plus Symbol
        '\x2d': '-',  # Hyphen Symbol
        '\x2e': '.',  # Period, dot, or full stop.
        '\x2f': '/',  # Forward Slash or divide symbol.
        '\x7c': '|',  # Vertical bar or pipe.
    }

    uri = {
        '%11': ',',  # Replacing Device Control 1 with a comma.
        '%12': '\n',  # Replacing Device Control 2 with a new line.
        '%20': ' ',  # Space
        '%22': '"',  # Double Quotes
        '%23': '#',  # Number Symbol
        '%27': '\'',  # Single Quote
        '%28': '(',  # Open Parenthesis
        '%29': ')',  # Close Parenthesis
        '%2B': '+',  # Plus Symbol
        '%2D': '-',  # Hyphen Symbol
        '%2E': '.',  # Period, dot, or full stop.
        '%2F': '/',  # Forward Slash or divide symbol.
        '%3A': ':',  # Colon
        '%7C': '|',  # Vertical bar or pipe.
    }

    for (enc, dec) in hexen.items():
        data = data.replace(enc, dec)

    for (enc, dec) in uri.items():
        data = data.replace(enc, dec)

    return data


def timethis(func):
    """
    Decorator that reports the execution time.
    Credit: andywalen
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper

def tob64(s):
    if type(s) is str:
        return base64.b64encode(s.encode('utf-8')).decode()

def fromb64(s):
    if type(s) is str:
        return base64.b64decode(s.encode('utf-8')).encode()

def getTimes(timeFrame):
    t=timeFrame
    now=datetime.now()
    times=tuple()

    if t is 'LAST_MINUTE' :
        times=(now-timedelta(seconds=60), now)
        
    elif t is 'LAST_10_MINUTES':
        times=(now-timedelta(minutes=10), now)

    elif t is 'LAST_30_MINUTES':
        times=(now-timedelta(minutes=30), now)

    elif t is 'LAST_HOUR':
        times=(now-timedelta(minutes=60), now)

    elif t is 'CURRENT_DAY':
        times=(now.replace(hour=0, minute=0, second=0), now.replace(hour=24, minute=59, second=59))

    elif t is 'PREVIOUS_DAY':
        yesterday=now-timedelta(hours=24)
        times=(yesterday.replace(hour=0, minute=0, second=0), yesterday.replace(hour=24, minute=59, second=59))

    elif t is 'LAST_24_HOURS':
        times=(now-timedelta(hours=24), now)

    elif t is 'LAST_2_DAYS':
        times=(now-timedelta(days=2), now)

    elif t is 'LAST_3_DAYS':
        times=(now-timedelta(days=3), now)

    else :
        raise ESMException("Timerange "+t+" is not supported for custom cumputation")
    
    return(times[0].isoformat(), times[1].isoformat())
    
    """
    elif t is 'CURRENT_WEEK':
        pass
    elif t is 'PREVIOUS_WEEK':
        pass
    elif t is 'CURRENT_MONTH':
        pass
    elif t is 'PREVIOUS_MONTH':
        pass
    elif t is 'CURRENT_QUARTER':
        pass
    elif t is 'PREVIOUS_QUARTER':
        pass
    elif t is 'CURRENT_YEAR':
        pass
    elif t is 'PREVIOUS_YEAR':
        pass"""

def regexMatch(regex, string):
    if re.search(regex, string):
        return True
    else:
        return False
