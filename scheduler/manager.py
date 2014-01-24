'''
Created on 2014.1.8

@author: gaolichuang@gmail.com
'''

from oslo.config import cfg

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

from cccrawler.manager import manager
from cccrawler.proto.crawldoc import CrawlDoc
from cccrawler.proto.crawldoc import OutLink

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class DummySchedulerManager(manager.CrawlManager):
    def __init__(self):
        super(DummySchedulerManager,self).__init__()
    def run_periodic_report_tasks(self,service):
        doc = CrawlDoc()
#        doc.request_url = 'http://roll.sohu.com/'
        doc.request_url = 'http://www.163.com/'
        doc.url = doc.request_url
        doc.level = 1
#        doc.outlinks.append(OutLink('url1','text1'))
#        doc.outlinks.append(OutLink('url2','text2'))
        self.output(doc)
