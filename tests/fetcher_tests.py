'''
Created on 2014.1.1

@author: gaolichuang
'''

import sys

from oslo.config import cfg

from miracle.common import config
from miracle.common.base import log as logging
from miracle.common.service import service
from miracle.common.service import multiservice
from cccrawler.fetcher import client
from cccrawler.proto.crawldoc import CrawlDoc

def main():
    config.parse_args(sys.argv)
    logging.setup("cccrawler")
    cl = client.Client()
    doc = CrawlDoc()
    doc.request_url = 'http://www.baidu.com/'
# doc.request_url = 'http://lavr.github.io/python-emails/tests/requests/some-utf8-text.html'
#    doc.request_url = 'http://roll.sohu.com/'
    doc.url = doc.request_url
    cl.process(doc)


if __name__ == '__main__':
    import sys 
    reload(sys)
    sys.setdefaultencoding('utf-8') 
    main()

