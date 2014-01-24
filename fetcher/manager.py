'''
Created on 2014.1.8

@author: gaolichuang
'''

from oslo.config import cfg

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

from cccrawler.manager import manager
from cccrawler.proto.crawldoc import CrawlDoc
from cccrawler.fetcher import client
CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class FetcherManager(manager.CrawlManager):
    def __init__(self):
        super(FetcherManager,self).__init__()
        self.client = client.Client()
    def ProcessCrawlDoc(self, crawldoc):
        LOG.debug(_("Before ProcessCrawldoc at %(fetch_id)s  crawldoc: %(crawldoc)s"),
                  {'fetch_id':self.m_id,
                   'crawldoc':crawldoc})
        self.client.process(crawldoc)
        print crawldoc.content
        LOG.debug(_("Before ProcessCrawldoc at %(fetch_id)s  crawldoc: %(crawldoc)s"),
                  {'fetch_id':self.m_id,
                   'crawldoc':crawldoc})

