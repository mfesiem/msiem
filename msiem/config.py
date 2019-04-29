# -*- coding: utf-8 -*-
"""
    msiem config
"""

from configparser import ConfigParser, NoSectionError, MissingSectionHeaderError
import os
import sys
from getpass import getpass
try:
    from .utils import log, tob64
    from .constants import DEFAULT_CONFIG_FILE, CONFIG_FILE_NAME
except ImportError :
    from utils import log, tob64
    from constants import DEFAULT_CONFIG_FILE, CONFIG_FILE_NAME

class ESMConfig(ConfigParser):
    """
    Find the config settings which include:
    
    [general]
    output=<text/json>
    verbose=<yes/no>
    ssl_verify=<yes/no>
    log_file=<path>

    [esm]
    host=<fqdn>
    user=<username>
    passwd=<b64password>
    
    
    ESMConfig(esm={'host':'10.2.2.1', 'user':'tristan'})
    """

    def __init__(self, path=None, **kwconfig):
        """
        Initialize the Config instance.
        """
        super().__init__()

        self._path=None

        if not path :

            path = self._find_ini_location()

            try :
                f=self.read(path)
                if len(f) == 0:
                    raise FileNotFoundError
            except :
                log.warning("Config file inexistant or currupted, applying defaults")
                self.read_string(DEFAULT_CONFIG_FILE)

            else :
                self._path = path

        if kwconfig :
            log.info("Applying config from manual specifications")
            for section in kwconfig :
                try :
                    if self.has_section(section):
                        for key in kwconfig[section] :
                            log.info("Setting ["+section+"] "+key+" = "+kwconfig[section][key])
                            self.set(section, key, kwconfig[section][key])
                    else:
                        log.warning("Skipping unknown config section "+section)

                    self.write()

                except Exception as err:
                    log.error("An error occured when reading the manual config dict. \n"+str(err))
                    raise
        
    def write(self, path=None):
        if not path :
            path=self._path
            if not path :
                path = self._find_ini_location()
        
        if path :
            try :
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                with open(path, 'w') as conf:
                    super().write(conf)

                self._path=path
                log.info("Config file wrote at "+path)

            except Exception as err :
                log.error("An error occured when writing the config file. \n"+str(err))
        else :
            log.error("Couldn't write config file, no specified path.")

    @staticmethod
    def _find_ini_location():
        """
        Attempt to locate the conf.ini file 
        """
        conf_path=None

        if 'APPDATA' in os.environ:
            conf_path = os.environ['APPDATA']

        elif 'XDG_CONFIG_HOME' in os.environ:  
            conf_path = os.environ['XDG_CONFIG_HOME']

        elif 'HOME' in os.environ:  
            conf_path = os.path.join(os.environ['HOME'])
    
       
        if conf_path  :
            conf_path=(os.path.join(conf_path, CONFIG_FILE_NAME))
            #log.info("Assuming config file at {}".format(conf_path))
        else :
            raise SystemError("Couldn't find either APPDATA, XDG_CONFIG_HOME or HOME environemnt variable to locate the conf.ini file.")

        return(conf_path)

    def setAuth(self):
        self.set('esm', 'host', input('Please enter the ESM FQDN: '))
        self.set('esm', 'user', input('Please enter your username: '))
        self.set('esm', 'passwd', tob64(getpass()))