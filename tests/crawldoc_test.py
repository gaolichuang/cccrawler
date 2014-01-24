'''
Created on 2014.1.5

@author: gaolichuang@gmail.com
'''
from cccrawler.proto import crawldoc
from cccrawler.utils import serialize
from cccrawler import utils


class Request(object):
    def __init__(self, url, method = 'GET', referer = None):
        self.url = url
        self.method = method
        self.referer = referer
    def FillByCrawlDoc(self, crawldoc):
        for name in vars(self).keys():
            if not name.startswith('__'):
                self.__dict__[name] = getattr(crawldoc, name)
    def __str__(self):
        return utils.ToStr(self)
class Response(object):
    def __init__(self,code):
        self.code = code
        self.history = []  # redirect history
#        self.last_modified = None
        self.header = {}
        self.content = ''
        self.content_type = None # get from http header like text/html
        self.redirect_url = None

        # get from analysis from content
        self.orig_encoding = None   # get from the metadata
        self.conv_encoding = 'utf-8'
    def FillCrawlDoc(self, crawldoc):
        for name in vars(self).keys():
            if not name.startswith('__'):
                crawldoc.__dict__[name] = getattr(self, name)
    def __str__(self):
        return utils.ToStr(self)


if __name__ == '__main__':
    doc = crawldoc.CrawlDoc()
    doc.request_url = 'afewoi'
    doc.outlinks.append(crawldoc.OutLink('url1','text1'))
    doc.outlinks.append(crawldoc.OutLink('url3','text3'))
    doc.outlinks.append(crawldoc.OutLink('url2','text2'))
    doc.reservation_dict = {'1':2}
    print doc
    adoc = crawldoc.CrawlDoc.restore(doc.convert)
    print adoc
    print(80*'=')
    doc_str = serialize.raw_serialize(doc.convert)
    print doc_str
    print type(doc_str)
    doc_convert = serialize.raw_deserialize(doc_str)
    print doc_convert
    print type(doc_convert)
    bdoc = crawldoc.CrawlDoc.restore(doc_convert)
    print bdoc
    print '='*80
    doc = crawldoc.CrawlDoc()
    doc.url = 'http://roll.sohu.com/'
    req = Request('aaaa')
    req.FillByCrawlDoc(doc)
    print req
    print '='*80
    resp = Response(400)
    print resp
    resp.FillCrawlDoc(doc)
    print doc
    
    