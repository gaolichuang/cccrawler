'''
Created on 2014.1.8

@author: gaolichuang
'''

from eventlet import greenthread

from oslo.config import cfg

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging
from miracle.common.utils import timeutils

from cccrawler.manager import manager
from cccrawler.fetcher import client
from cccrawler.fetcher import hostload

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class FetcherManager(manager.CrawlManager):
    def __init__(self):
        super(FetcherManager,self).__init__()
        self.client = client.Client()
        self.hostload = hostload.Hostload()
    def ProcessCrawlDoc(self, crawldoc):
        host = crawldoc.host
        if crawldoc.fake_host: host = crawldoc.fake_host
        delay = self.hostload.readyForFetch(host)
        LOG.debug(_("Before ProcessCrawldoc sleep %(sleep)s at %(fetch_id)s  crawldoc: %(crawldoc)s"),
                  {'sleep':delay,
                   'fetch_id':self.m_id,
                   'crawldoc':crawldoc})        
        greenthread.sleep(delay)
        self.client.process(crawldoc)
        print crawldoc.content
        crawldoc.crawl_time = timeutils.utcnow_ts()
        LOG.debug(_("Before ProcessCrawldoc at %(fetch_id)s  crawldoc: %(crawldoc)s"),
                  {'fetch_id':self.m_id,
                   'crawldoc':crawldoc})

