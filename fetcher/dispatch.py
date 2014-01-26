'''
Created on 2014.1.1

@author: gaolichuang
'''

import random
import mmh3 # https://github.com/gaolichuang/mmh3

from oslo.config import cfg
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging
from cccrawler.fetcher import hostload
from cccrawler.utils import urlutils
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
        self.hostload = hostload.Hostload()
    def dispatch(self,crawldoc):
        # fill fake host
        try:
            crawldoc.fake_host = self.hostload.fakeHost(crawldoc.host)
            LOG.debug(_("Fill fake host from: %(host)s to %(fakehost)s"),
                        {'host':crawldoc.host,
                         'fakehost':crawldoc.fake_host})
        except:
            crawldoc.fake_host = None
        disp = getattr(self, 'dispatch_as_%s'%CONF.dispatch_as)
        return disp(crawldoc)

    def dispatch_as_host(self,crawldoc):
        '''TODO: only dispatch as host support multi fetcher
                if has fake_host, use fake_host'''
        if crawldoc.fake_host != None:
            host = crawldoc.fake_host
        else:
            host = crawldoc.host
        fp = mmh3.hash(host)
        index = (fp % CONF.fetcher_number + self.hostload.multifetchOffset(host)) % CONF.fetcher_number
        return index
    def dispatch_as_domain(self,crawldoc):
        domain = urlutils.getdomain(crawldoc.url)
        fp = mmh3.hash(domain)
        return fp % CONF.fetcher_number
    def dispatch_as_url(self,crawldoc, random = False):
        if random:
            return random.randint(0, CONF.fetcher_number - 1)
        fp = mmh3.hash(crawldoc.url)
        return fp % CONF.fetcher_number
