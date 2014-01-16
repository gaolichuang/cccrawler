'''
Created on 2014.1.5

@author: gaolichuang
'''

import json

def raw_serialize(raw_msg):
    ''' python dict to json object(python str)
    return string'''
    return json.dumps(raw_msg)

def raw_deserialize(msg):
    return json.loads(msg)