'''
Created on 2014.2.8

@author: gaolichuang@gmail.com

de weight by keys
'''
from miracle.common.base import memcache

_unique_client = None

def get_client():
    global _unique_client
    if _unique_client == None:
        _unique_client = UniqueKey()
    return _unique_client

class UniqueKey(object):
    def __init__(self):
        self.mc = memcache.get_client()
    def unique(self,keys):
        ''' key:value ==  key:1'''
        fresh_keys = []
        for key in keys:
            if not self.has(key):
                fresh_keys.append(key)
        return fresh_keys
    def has(self,key):
        if None == self.mc.get(key):
            self.mc.add(key,'1')
            return False
        return True

if __name__ == '__main__':
    pass