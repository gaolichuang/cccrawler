'''
Created on 2014.1.8

@author: gaolichuang@gmail.com
'''

from oslo.config import cfg
import mmh3 # https://github.com/gaolichuang/mmh3
import os

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

from cccrawler.manager import manager
from cccrawler.proto.crawldoc import CrawlDoc
from cccrawler.proto.crawldoc import OutLink
from cccrawler.proto.db import api as db_api
from cccrawler.utils import urlutils
from cccrawler.handler import urlfilter

scheduler_opt = [
    cfg.IntOpt('max_level',
               default=1,
               help='how deep do you want to crawl'),
    cfg.IntOpt('max_fail_retry_time',
               default=2,
               help='crawl fail retry time'),
    cfg.IntOpt('max_timeout_retry_time',
               default=2,
               help='crawl timeout retry time'),
    cfg.IntOpt('read_batch_num',
               default=80,
               help='read batch number like db limit'),
    cfg.IntOpt('crawl_timeout',
               default=3600,
               help='time out interval'),
    cfg.StrOpt('init_url',
               default='',
               help='init url to crawl'),
    cfg.StrOpt('init_url_file',
               default='',
               help='init url file to crawl'),
]

CONF = cfg.CONF
CONF.register_opts(scheduler_opt)

LOG = logging.getLogger(__name__)

class DummySchedulerManager(manager.CrawlManager):
    def __init__(self):
        super(DummySchedulerManager,self).__init__()
    def run_periodic_report_tasks(self,service):
        '''TODO: fill url host level and something
            make some nessary check'''
        doc = CrawlDoc()
        doc.request_url = 'http://roll.sohu.com/'
#        doc.request_url = 'http://www.163.com/'
        doc.url = doc.request_url
        doc.docid = mmh3.hash(doc.url)
        doc.level = 1
        doc.host = 'roll.sohu.com'
#        doc.outlinks.append(OutLink('url1','text1'))
#        doc.outlinks.append(OutLink('url2','text2'))
        self.output(doc)


class ExportSchedulerManager(manager.CrawlManager):
    def __init__(self):
        super(ExportSchedulerManager,self).__init__()
        self.max_level = CONF.max_level
        self.max_fail_retry_time = CONF.max_fail_retry_time
        self.max_timeout_retry_time = CONF.max_timeout_retry_time
        self.read_batch_num = CONF.read_batch_num
        self.crawl_timeout = CONF.crawl_timeout
        
        self.filter = urlfilter.Filter()
    def run_periodic_report_tasks(self,service):
        '''TODO: Read from database'''
        ''' get fresh crawldoc'''
        self.wait_for_outputqueue_ready()
        docs = db_api.getFreshCrawlDoc(self.read_batch_num, self.max_level)
        if len(docs) < self.read_batch_num * 0.5:
            ''' get fresh timeout crawldoc '''
            timeout_docs = db_api.getTimeoutCrawlDoc(
                                    self.crawl_timeout,self.max_timeout_retry_time,
                                    self.read_batch_num)
            docs = docs + timeout_docs
            if len(docs) < self.read_batch_num * 0.5:
                ''' get crawl fail crawldoc '''
                fail_docs = db_api.getFailCrawlDoc(self.max_fail_retry_time,
                                               self.read_batch_num)
                docs = docs + fail_docs
                if len(docs) < self.read_batch_num * 0.5:
                    ''' get crawl fail timeout crawldoc'''
                    fail_docs = db_api.getTimeoutFailCrawlDoc(self.crawl_timeout,
                                            self.max_fail_retry_time + self.max_timeout_retry_time,
                                            self.read_batch_num)
        for doc in docs:
            if not self.filter.Legalurl(doc.request_url):
                LOG.error(_('UnLegalurl  crawldoc %(crawldoc)s'),{'crawldoc':doc})
                continue
            doc.url = urlutils.normalize(doc.request_url)
            doc.docid = mmh3.hash(doc.url)
            doc.host = urlutils.gethost(doc.url)
            self.output(doc)
    def Run(self, context, *args, **kwargs):
        '''TODO: save url to pending db'''
        urls = []
        if not self.filter.Legalurl(CONF.init_url):
            urls.append(CONF.init_url)
        if CONF.init_url_file != '' and os.path.exists(CONF.init_url_file):
            with open(CONF.init_url_file, 'r') as fp:
                lines = fp.readlines()
                for line in lines:
                    if not self.filter.Legalurl(line):
                        urls.append(line)
        for url in urls:
            db_api.addPendingCrawlDoc(url, 0, 0)
            LOG.info(_('Add init url %(url)s'),{'url':url})
