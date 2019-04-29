#!/bin/env python3
#requirement : pip3 install requests

import requests
import base64
from getpass import getpass
from urllib.parse import urljoin
import time
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE_URL = 'https://{}/rs/esm/'.format(input('Please enter the ESM FQDN: '))
HEADERS={'Content-Type': 'application/json'}
CONFIG={"config":{
        "timeRange": "LAST_30_MINUTES", 
        "fields": [{"name": "AvgSeverity"}, {"name": "DstPort"}, {"name": "DstMac"}, {"name": "SrcIP"}, {"name": "DSIDSigID"}, {"name": "SrcMac"}, {"name": "DstIP"}, {"name": "SrcPort"}, {"name": "LastTime"}],
        "filters": [{"type": "EsmFieldFilter", "field": {"name": "DstIP"},"operator": "IN", "values": [{"type": "EsmBasicValue", "value": "10.0.0.0/8"}]}],
        "limit": 1,
        "offset": None
        }
    }


def tob64(s):
    return base64.b64encode(s.encode('utf-8')).decode()

def post(method, data):
    print("POSTING "+str(method)+" "+str(json.dumps(data)))
    return requests.post(
            urljoin(BASE_URL, method),
            data=json.dumps(data), 
            headers=HEADERS,
            verify=False,
            timeout=15
        )
    

def login(user, passwd):
        logged = post('login', {'username':user, 'password':passwd, "locale": "en_US"} )
        
        HEADERS['Cookie'] = logged.headers.get('Set-Cookie')
        HEADERS['X-Xsrf-Token'] = logged.headers.get('Xsrf-Token')
        
        if "Issue validating session token." in post('/','').text :
            raise Exception("Login failed")

def wait(id):
    status={'complete':False}
    while True :
        status = post('qryGetStatus', {"resultID": id}).json()['return']
        if status['complete']:
            return
        else :
            time.sleep(0.5)

user = tob64(input('Please enter your username: '))
passwd = tob64(getpass())

login(user, passwd)

CONFIG['config']['offset']=0
id1 = post('qryExecuteDetail?type=EVENT&reverse=false', CONFIG).json()['return']['resultID']

CONFIG['config']['offset']=50
id2 = post('qryExecuteDetail?type=EVENT&reverse=false', CONFIG).json()['return']['resultID']

#print(id1.text)
#print(id2.text)

wait(id1)
wait(id2)

print("Result #1 {}".format(post('qryGetResults?startPos=0&numRows=1&reverse=false', {"resultID": id1}).text))
print("Result #2 {}".format(post('qryGetResults?startPos=0&numRows=1&reverse=false', {"resultID": id2}).text))