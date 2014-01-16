'''
Created on 2014.1.1

@author: gaolichuang
'''

import random

from oslo.config import cfg
from eventlet import greenthread
from miracle.common.manager import periodic_task
from miracle.common.manager.managercontainer import ManagerContainer
from miracle.common.base import log as logging

dispatcher_opts = [
    cfg.StrOpt('dispatch_as',
               default='host',
               help='host url or domain for dispatch')
]

CONF = cfg.CONF
CONF.register_opts(dispatcher_opts)
''' import_opt should behind  define, attention when you use import'''
CONF.import_opt('fetcher_number', 'cccrawler.fetcher.managercontainer')

LOG = logging.getLogger(__name__)

class Dispatcher(object):
    def __init__(self):
        pass
    def dispatch(self,crawldoc):
        disp = getattr(self, 'dispatch_as_%s'%CONF.dispatch_as)
        return disp(crawldoc)

    def dispatch_as_host(self,crawldoc):
        '''TODO: add logic'''
        return random.randint(0, CONF.fetcher_number - 1)
    def dispatch_as_domain(self,crawldoc):
        '''TODO: add logic'''
        return random.randint(0, CONF.fetcher_number - 1)
    def dispatch_as_url(self,crawldoc):
        '''TODO: add logic'''
        return random.randint(0, CONF.fetcher_number - 1)
