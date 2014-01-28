'''
Created on 2014.1.8

@author: gaolichuang
'''
import time

from oslo.config import cfg

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

from cccrawler.manager import manager
from cccrawler.proto.crawldoc import CrawlDoc
from cccrawler.handler import htmlparser
from cccrawler.proto.db import api as db_api
from cccrawler import utils
CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class DummyHandlerManager(manager.CrawlManager):
    def __init__(self):
        super(DummyHandlerManager,self).__init__()

    def ProcessCrawlDoc(self,crawldoc):
        LOG.debug(_('Get one crawldoc at %(name_)s %(handler_id)s crawldoc %(crawldoc)s'),
                  {'name_':self.__class__.__name__,
                   'handler_id':self.m_id,
                   'crawldoc':crawldoc})

class HandlerManager(manager.CrawlManager):
    def __init__(self):
        super(HandlerManager,self).__init__()
        self.htmlparser = htmlparser.Parser()
    def ProcessCrawlDoc(self,crawldoc):
        LOG.debug(_('Get one crawldoc at %(name_)s %(handler_id)s crawldoc %(crawldoc)s'),
                  {'name_':self.__class__.__name__,
                   'handler_id':self.m_id,
                   'crawldoc':crawldoc})
        self.htmlparser.process(crawldoc)
        LOG.debug(_('Finish Process one crawldoc at %(name_)s %(handler_id)s crawldoc %(crawldoc)s'),
                  {'name_':self.__class__.__name__,
                   'handler_id':self.m_id,
                   'crawldoc':crawldoc})
        start_time = time.time()
        if utils.IsCrawlSuccess():
            db_api.saveSuccessCrawlDoc(crawldoc)
            LOG.debug(_('Finish Save Success Crawldoc to DB use %(cost)s'),
                        {'cost':(time.time()-start_time)})
        else:
            db_api.saveFailCrawlDoc(crawldoc)
            LOG.debug(_('Finish Save Success Crawldoc to DB use %(cost)s'),
                        {'cost':(time.time()-start_time)})            
            

