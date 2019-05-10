# -*- coding: utf-8 -*-
"""
    msiem config
"""

from configparser import ConfigParser, NoSectionError, MissingSectionHeaderError
import os
import sys
from getpass import getpass
from .utils import tob64
from .constants import DEFAULT_CONFIG_FILE, CONFIG_FILE_NAME



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

        if not path :
            self._path = self._find_ini_location()

        else : 
            self._path = path

        try :
            f=self.read(self._path)
            if len(f) == 0:
                raise FileNotFoundError

        except :
            print("Config file inexistant or currupted, applying defaults")

            if not os.path.exists(os.path.dirname(self._path)):
                os.makedirs(os.path.dirname(self._path))

            with open(self._path, 'w') as conf :
                conf.write(DEFAULT_CONFIG_FILE)

            self.read(self._path)
            self.write()

        if kwconfig :
            for section in kwconfig :
                try :
                    if self.has_section(section):
                        for key in kwconfig[section] :
                            #log.info("Setting ["+section+"] "+key+" = "+kwconfig[section][key])
                            self.set(section, key, kwconfig[section][key])
                    else:
                        pass
                        #log.warning("Skipping unknown config section "+section)

                except Exception as err:
                    raise Exception("An error occured when reading the manual config dict. \n"+str(err))
        
    def write(self, path=None):
        if not path :
            path=self._path
            if not path :
                path = self._find_ini_location()
        
        if path :
            try :
                with open(path, 'w') as conf:
                    super().write(conf)

                self._path=path
                print("Config file wrote at "+path)

            except Exception as err :
                raise Exception("An error occured when writing the config file. \n"+str(err))
        else :
            raise Exception("Couldn't write config file, no specified path.")

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

    def set(self, section, option, value=None):
        if value == '' :
            pass
        else:
            super().set(section, option, value)

    def iset(self, msg, section, option):
        value = self.get(section, option)
        newvalue=''
        if option is 'passwd' :
            newvalue = tob64(getpass(msg+ '. Press <Enter> to skip: '))
        else:
            newvalue = input(msg+ '. Press <Enter> to keep '+ (value if (str(value) is not '') else 'empty') + ': ')
        self.set(section, option, newvalue)
        
    def interactiveSet(self):
        self.iset('Enter ESM hostname', 'esm', 'host')
        self.iset('Enter ESM username', 'esm', 'user')
        self.iset('Enter ESM password', 'esm', 'passwd')
        self.write()

    def show(self):
        print('Configuration file : '+self._path+'\n'+open(self._path, 'r').read())