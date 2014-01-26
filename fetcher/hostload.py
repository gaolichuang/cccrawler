'''
Created on 2014.1.25

@author: gaolichuang@gmail.com
'''
import re
import os

from oslo.config import cfg
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging
from miracle.common.utils import timeutils
from cccrawler.utils import loadConfToDict

hostload_opts = [
    cfg.IntOpt('default_hostload',
               default=5,
               help='default host load for fetch'),
    cfg.IntOpt('reload_conf_interval',
               default=3600,
               help='reload conf interval'),
    cfg.ListOpt('fake_host',
               default=[],
               help='fake host list, format[\'\d+\.blog\.sina\.com,XXXX.blog.sina.com\',]'
                    ' first field is re2, second is the normalized fake host, use for extensive domain'
                    'use for dispatch'),
    cfg.StrOpt('fake_host_file',
               default='',
               help='same with fake host but at file'
                    'format: \d+\.blog\.sina\.com,XXXX.blog.sina.com'),
    cfg.ListOpt('hostload_exception',
               default=[],
               help='host load exception conf, format: [\'host name, hostload\',]'
                    'like [\'roll.sohu.com,3\',]),'
                    'use for fetch delay'),
    cfg.StrOpt('hostload_exception_file',
               default='',
               help='same with hostload_exception but at file'),
    cfg.ListOpt('multi_fetch',
               default=[],
               help='host load exception conf, format: [\'host name, multi_fetch\',]'
                    'like [\'roll.sohu.com,2\',]),'
                    'use for dispatch'),
    cfg.StrOpt('multi_fetch_file',
               default='',
               help='same with multi_fetch but at file'),
]

CONF = cfg.CONF
CONF.register_opts(hostload_opts)

LOG = logging.getLogger(__name__)

class Hostload(object):
    '''TODO: 
        1.the hostload only support host name not url pattern'''
    def __init__(self):
        self.fake_host = {}
        self.hostload_exception = {}
        '''TODO: if has too much host, hostload_delay dict will too big!!'''
        self.hostload_delay = {}
        self.default_hostload = CONF.default_hostload
        self.multifetch = {}
        self.multifetch_offset = {}
        self.last_reload = 0
        self.loadConf()

    def fakeHost(self,host):
        '''call by dispatcher'''
        self.loadConf()
        for pattern,value in self.fake_host.items():
            if pattern.match(host):
                return value
        raise Exception
    def loadConf(self):
        if int(timeutils.utcnow_ts()) - self.last_reload < CONF.reload_conf_interval:
            return
        self.last_reload = int(timeutils.utcnow_ts())
        ## load fakehost
        fake_host_dict = {}
        loadConfToDict(fake_host_dict,CONF.fake_host,
                       CONF.fake_host_file,'FakeHost')
        for key,value in fake_host_dict.items():
            rkey = re.compile(key)
            self.fake_host[rkey] = value

        ## load host load exception
        loadConfToDict(self.hostload_exception,CONF.hostload_exception,
                       CONF.hostload_exception_file,'HostLoadException')
        ## load multi fetcher
        loadConfToDict(self.multifetch,CONF.multi_fetch,CONF.multi_fetch_file,'Multifetch')
        for key in self.multifetch.keys():
            self.multifetch_offset[key] = 0

    def multifetchOffset(self,host):
        '''call by dispatch_as_host in dispatcher'''
        if host in self.multifetch:
            index = self.multifetch_offset[host] % self.multifetch[host]
            self.multifetch_offset[host] = (self.multifetch_offset[host] + 1) % self.multifetch[host]
            return index
        return 0;
    def readyForFetch(self, nhost):
        '''param: nhost(normalize_hostname), if has fake_host, use fake_host
            return sleep time
            use in fetcher manager for sleep'''
        delay = 0
        if nhost in self.hostload_delay.keys():
            if nhost in self.hostload_exception.keys():
                interval = self.hostload_exception[nhost]
            else:
                interval = self.default_hostload
            LOG.debug(_("Get hostload interval host: %(host)s, interval:%(interval)s"),
                        {'host':nhost,'interval':interval})
            now = int(timeutils.utcnow_ts())
            if now - self.hostload_delay[nhost] < interval:
                delay = interval + self.hostload_delay[nhost] - now
                LOG.debug(_("Interval not arrive for host: %(host)s,"
                            " now:%(now)s delay:%(delay)s last delay:%(last)s"),
                            {'host':nhost,'now':now,'delay':delay,
                             'last':self.hostload_delay[nhost]})                       
            self.hostload_delay[nhost] = int(timeutils.utcnow_ts())
        else:
            self.hostload_delay[nhost] = int(timeutils.utcnow_ts())
            LOG.debug(_("Add host: %(host)s, delay:%(delay)s"),
                        {'host':nhost,'delay':self.hostload_delay[nhost]})            
        if delay < 0: delay = 0
        return delay
    
    
if __name__ == '__main__':
    pass
