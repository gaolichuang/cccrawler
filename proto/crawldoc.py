'''
Created on 2014.1.5

@author: gaolichuang@gmail.com
'''
import copy

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
        # fill by export scheduler
        self.request_url = None
        self.reservation_dict = {}
        self.parent_docid = None
        self.level = 0  # start from 0
        self.detect_time = 0 # when to crawl come from scheduler
        self.pending_id = None # get from pending database
        # fill by scheduler
        self.url= None  # nomalize from self.request_url
        self.docid = None   # url fingerprint, use MurmurHash  https://pypi.python.org/pypi/mmh3/2.2
        self.host = None # save calculate

        # use for fetch fill at dispatch
        self.fake_host = None # use for hostload
        
        # crawl meta, use for custom crawl
        self.method = 'GET' # default is get
        self.referer = None
        self.custom_accept_types = None

        # get from http
        self.code = None
        self.reason = None
        self.history = []  # redirect history
#        self.last_modified = None
        self.header = {}
        self.content = ''
        self.content_type = None # get from http header like text/html
        self.redirect_url = None

        self.crawl_time = None # fill at fetcher

        # get from analysis from content
        self.orig_encoding = None   # get from the metadata
        self.conv_encoding = 'utf-8'
        '''
        TODO:language does not implementation, you can use nltk to do this, need word dict
        http://blog.alejandronolla.com/2013/05/15/detecting-text-language-with-python-and-nltk/
        '''
        #self.language = None
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
        show_dict = copy.copy(self.convert)
        show_dict['content'] = '_CLEAN_UP_'
        return str(sorted(show_dict.items(),key=lambda e:e[1],reverse=True))
