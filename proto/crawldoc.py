'''
Created on 2014.1.5

@author: gaolichuang@gmail.com
'''

class AbstractObject(object):
    @property
    def convert(self):
        '''use for serialize to dict'''
        raw_dict = {}
        for name,value in vars(self).items():
#            print('%s=%s'%(name,value))
            if  isinstance(value, list):
                raw = []
                for ol in value:
                    try:
                        raw.append(ol.convert)
                    except:
                        raw.append(ol)
                raw_dict[name] = raw
            elif isinstance(value, dict):
                raw = {}
                for k in value.keys():
                    try:
                        raw[k] = value[k].convert
                    except:
                        raw[k] = value[k]
                raw_dict[name] = raw
            else:
                try:
                    raw_dict[name] = value.convert
                except:
                    raw_dict[name] = value
        return raw_dict  
    @classmethod
    def restore(cls,raw_dict):
        return cls(raw_dict)

class OutLink(AbstractObject):
    def __init__(self,url=None,text=None, **entries):
        self.url = url
        self.text = text
        self.__dict__.update(entries)

     
class CrawlDoc(AbstractObject):
    def __init__(self, entries = {}):
        self.request_url = None
        self.url= None  # nomalize from self.request_url
        self.docid = None   # url fingerprint, use MurmurHash  https://pypi.python.org/pypi/mmh3/2.2
        self.reservation_dict = {}
        # the time when this doc is fetched, in seconds of UTC time.
        self.timestamp = None
        self.parent_url = None
        self.level = 0  # start from 0

        # get from http
        self.code = None
        self.redirect_url = None
        self.last_modified = None
        self.content_encoding = None
        self.header = None
        self.header_content_length = None
        self.content = ''
        self.content_length = None

        # get from analysis from content
        self.orig_encoding = None
        self.conv_encoding = None
        self.language = None
        self.outlinks = []

        self.__dict__.update(entries) # update var dict
        ''' dict list var should rewrite here!'''
        raw_outlinks = self.outlinks
        self.outlinks = []
        for ol in raw_outlinks:
            try:
                self.outlinks.append(ol.restore())
            except:
                self.outlinks.append(ol)
        raw = self.reservation_dict
        self.reservation_dict = {}
        for ol in raw.keys():
            try:
                self.reservation_dict[ol] = raw[ol].restore()
            except:
                self.reservation_dict[ol] = raw[ol]

    def __str__(self):
        return str(sorted(self.convert.items(),key=lambda e:e[1],reverse=True))