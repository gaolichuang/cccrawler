'''
Created on 2014.1.5

@author: gaolichuang@gmail.com
'''
from cccrawler.proto import crawldoc
from cccrawler.base import serialize

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
