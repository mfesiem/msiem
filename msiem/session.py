# -*- coding: utf-8 -*-
"""
    msiem session
"""
import ast
import re
import base64
import requests
import urllib3
import json
import getpass
import ssl
from urllib.parse import urljoin, unquote
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from abc import ABC
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .params import PARAMS
from .constants import BASE_URL, BASE_URL_PRIV, ASYNC_MAX_WORKERS, GENERAL_POST_TIMEOUT
from .exceptions import ESMException
from .utils import tob64, getLogger
from .config import ESMConfig
        

class ESMSession():

    """
        # static variables
        _headers={'Content-Type': 'application/json'}
        _executor = ThreadPoolExecutor(max_workers=ASYNC_MAX_WORKERS)

        _config=None
    

    #Singleton : unique instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        if ESMSession._instance is None :
            self._logger.debug('Creating a new instance of ESMSession')
            ESMSession._instance = ABC.__new__(cls, *args, **kwargs)

        return ESMSession._instance
        """

    _initiated = False
    _shared_state = {}

    def __init__(self, conf_path=None, **config):
        self.__dict__ = self._shared_state
        if not self._initiated :
            #Config parsing
            self._config = ESMConfig(path=conf_path, **config)
            self._logger = getLogger(v=self._config.getboolean('general', 'verbose'))
            self._executor = ThreadPoolExecutor(max_workers=ASYNC_MAX_WORKERS)
            self._headers={'Content-Type': 'application/json'}
            self._logged=False
            self._initiated = True
            
    def __str__(self):
        return repr(self)

    def _login(self):
        
        userb64 = tob64(self._config.get('esm', 'user'))
        passb64 = self._config.get('esm', 'passwd')
        
        try :
            resp = self.esmRequest('login', username=userb64, password=passb64, raw=True, secure=True)
            self._headers['Cookie'] = resp.headers.get('Set-Cookie')
            self._headers['X-Xsrf-Token'] = resp.headers.get('Xsrf-Token')
        
        except Exception :
            raise ESMException("Login failed")

        else :
            return True

    """
    def logout(self):
        self.esmRequest('logout')
        
    """

    def esmRequest(self, method, callback=None, raw=False, secure=False, **params):

        self._logger.debug("Calling esmRequest with params :"+str(params))

        method, data = PARAMS.get(method)

        if data :
            data =  data % params
            data = ast.literal_eval(''.join(data.split()))
        
        if method :
            method = method % params

        post=dict()

        if not self._logged and method != 'login':
            self._logged=self._login()

        try :
            post = self._post(method, data, callback, raw, secure)
            return post

        except Exception as err:
            self._logger.error(str(err))
            raise err

    def _post(self, method=None, data=None, callback=None, raw=False, secure=False):
        """
        Helper method
        If method is all upper cases, a private API is done.
        Private API is under /ess/ and public api is under /rs/esm
        """

        url=str()
        privateApiCall=False
        result=None

        #Handling private API calls formatting
        if method == method.upper():
            privateApiCall=True
            url = BASE_URL_PRIV
            if data :
                data = self._format_params(method, **data)
        
        #Normal API calls
        else:
            url = BASE_URL
            if data:
                data = json.dumps(data)

        self._logger.debug('POSTING : ' + method + ('\nDATA'+(data if data is not None else '') if not secure else ''))
        #self._logger.debug(self.__dict__)

        try :
            result = requests.post(
                urljoin(url.format(self._config.get('esm', 'host')), method),
                data=data, 
                headers=self._headers,
                verify=self._config.getboolean('general','ssl_verify'),
                timeout=GENERAL_POST_TIMEOUT
            )

            if not secure :
                pass
                #self._logger.debug('RESULT : '+result.text)

            if raw :
                return result

            else:
                try:
                    result.raise_for_status()

                except requests.HTTPError as e :
                    self._logger.error(str(e)+' '+str(result.text))

                else: #
                    try:
                        result = result.json()
                        result = result.get('return')

                    except json.decoder.JSONDecodeError:
                        result = result.text

                    if privateApiCall :
                        result = self._format_priv_resp(result)

                    if callback:
                        result = callback(result)

                    return result

        except ConnectionError as e:
            self._logger.critical(e)
            raise
        except requests.exceptions.Timeout as e:
            self._logger.error(e)
            pass
        except requests.exceptions.TooManyRedirects as e :
            self._logger.error(e)
            pass
        except Exception as e:
            self._logger.error(e)
        
    @staticmethod
    def _format_params(cmd, **params):
        """
        Format private API call.
        From mfe_saw project at https://github.com/andywalden/mfe_saw
        """
        params = {k: v for k, v in params.items() if v is not None}
        params = '%14'.join([k + '%13' + v + '%13' for (k, v) in params.items()])
        
        if params:
            params = 'Request=API%13' + cmd + '%13%14' + params + '%14'
        else:
            params = 'Request=API%13' + cmd + '%13%14'
        return params

    @staticmethod
    def _format_priv_resp(resp):
        """
        Format response from private API
        From mfe_saw project at https://github.com/andywalden/mfe_saw
        """
        resp = re.search('Response=(.*)', resp).group(1)
        resp = resp.replace('%14', ' ')
        pairs = resp.split()
        formatted = {}
        for pair in pairs:
            pair = pair.replace('%13', ' ')
            pair = pair.split()
            key = pair[0]
            if key == 'ITEMS':
                value = pair[-1]
            else:
                value = unquote(pair[-1])
            formatted[key] = value
        return formatted

class ESMObject(ABC):

    def __init__(self):
        self._session = ESMSession()

    def esmRequest(self, *args, **kwargs):
        return self._session.esmRequest(*args, **kwargs)
    

