# -*- coding: utf-8 -*-
"""
mfesaw2 exceptions
"""

class ESMException(Exception):
    """Base Exception"""
    pass

class ESMDataSourceNotFound(ESMException):
    """Raised when the ESM returns an error while: 
    'deserializing ESMDataSourceDetail"""
    pass

class ESMParamsError(ESMException):
    pass

class ESMAuthError(ESMException):
    pass