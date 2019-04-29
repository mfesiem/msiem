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
from .utils import log, tob64
from .config import ESMConfig

class ESMSession(ABC):

    # static variables
    _headers={'Content-Type': 'application/json'}
    _executor = ThreadPoolExecutor(max_workers=ASYNC_MAX_WORKERS)
    _logged=False
    _config=None

    def __init__(self, conf_path=None, **config):

        #Config parsing
        ESMSession._config = ESMConfig(path=conf_path, **config)
        
        #singleton attributes mapping
        self._config=ESMSession._config
        self._executor = ESMSession._executor
        self._headers=ESMSession._headers
        self._logged=ESMSession._logged

    def __str__(self):
        return repr(self)

    def login(self):
        userb64 = tob64(self._config.get('esm', 'user'))
        passb64 = self._config.get('esm', 'passwd')
        
        resp = self.esmRequest('login', username=userb64, password=passb64, raw=True, secure=True)
        
        try :
            self._headers['Cookie'] = resp.headers.get('Set-Cookie')
            self._headers['X-Xsrf-Token'] = resp.headers.get('Xsrf-Token')

            self._logged = True

            if self.esmRequest('get_user_locale') == False :

                self._logged = False
                log.error("Failed to login ")
                raise ESMException("Login failed")

        except Exception as err :
            log.error("Failed to login \n"+str(err))
            raise ESMException("Login failed")

    @property
    def logged(self):
        return self._logged
        #return (not self.esmRequest('get_user_locale') == False)

    def logout(self):
        self.esmRequest('logout')
        self._logged=False

    def esmRequest(self, method, callback=None, raw=False, secure=False, asynch=True, **params):

        if not self.logged and method is not 'login' :
            self.login()

        method, data = PARAMS.get(method)

        if data :
            data =  data % params
            data = ast.literal_eval(''.join(data.split()))
        
        if method :
            method = method % params

        post=dict()

        try :
            post = self._post(method, data, callback, raw, secure, asynch)
            return post

        except Exception as err:
            log.error(str(err))
            return False

    def _post(self, method=None, data=None, callback=None, raw=False, secure=False, asynch=True):
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

        if data and not secure :
            log.debug('DATA : '+data)

        try :
            if asynch :
                future = self._executor.submit(
                    requests.post, 
                    urljoin(url.format(self._config.get('esm', 'host')), method),
                    data=data, 
                    headers=ESMSession._headers,
                    verify=self._config.getboolean('general','ssl_verify'),
                    timeout=GENERAL_POST_TIMEOUT
                    )

                result = future.result()

            elif not asynch :
                result = requests.post(
                    urljoin(url.format(self._config.get('esm', 'host')), method),
                    data=data, 
                    headers=ESMSession._headers,
                    verify=self._config.getboolean('general','ssl_verify'),
                    timeout=GENERAL_POST_TIMEOUT
                )

            if not secure :
                pass
                #log.debug('RESULT : '+result.text)

            if raw :
                return result

            else:
                try:
                    result.raise_for_status()

                except requests.HTTPError as e :
                    log.error(str(e)+' '+str(result.text))

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
            log.critical(e)
            raise
        except requests.exceptions.Timeout as e:
            log.error(e)
            pass
        except requests.exceptions.TooManyRedirects as e :
            log.error(e)
            pass
        except Exception as e:
            log.error(e)
        
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