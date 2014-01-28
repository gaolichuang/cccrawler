'''
Created on 2014.1.24

@author: gaolichuang
'''
import urlparse
import re
import os

from oslo.config import cfg
from cccrawler.utils import urlutils
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging 
from miracle.common.utils import timeutils
urlfilter_opts = [
    cfg.ListOpt('domain_whitelist',
                default=['com','cn','org','hk','edu','net','biz'],
                help = 'domain white list'),
    cfg.BoolOpt('use_url_whitelist',
                default=False,
                help = 'use url whitelist to filter or not'),
    cfg.ListOpt('url_whitelist',
                default=[],
                help = 'url re2 patterns'),
    cfg.StrOpt('url_whitelist_filename',
                default='',
                help = 'url re2 patterns filename'),
    cfg.IntOpt('reload_url_filter_interval',
                default=3600,
                help = 'reload whitelist file'),                  
]

CONF = cfg.CONF
CONF.register_opts(urlfilter_opts)
LOG = logging.getLogger(__name__)

class Filter(object):
    def __init__(self,url_whitelist_filename = None,domain_whitelist = None,
                 use_url_whitelist = None,url_whitelist = None):
        self.patterns = set()
        self.last_load = 0.0
        self.url_whitelist_filename = url_whitelist_filename
        if self.url_whitelist_filename == None:
            self.url_whitelist_filename = CONF.url_whitelist_filename
        self.domain_whitelist = domain_whitelist
        if self.domain_whitelist == None:
            self.domain_whitelist = CONF.domain_whitelist
        self.use_url_whitelist = use_url_whitelist
        if self.use_url_whitelist == None:
            self.use_url_whitelist = CONF.use_url_whitelist
        self.url_whitelist = url_whitelist
        if self.url_whitelist == None:
            self.url_whitelist = CONF.url_whitelist
    def Legalurl(self,url):
        if url.startswith('http'):
            return True
        return False
    def filter(self,url):
        self.load(self.url_whitelist_filename)
        if self.filterbydomain(url):
            return True,'FilterByTopDomain'
        if self.filterbyurl(url):
            return True,'FilterByUrlWhitelist'
        return False,''

    def filterbydomain(self,url):
        topdomain = urlutils.gettopdomain(url)
        return not topdomain in self.domain_whitelist
    def filterbyurl(self,url):
        if not self.use_url_whitelist:
            return False
        if len(self.patterns) == 0:
            return True
        for pattern in self.patterns:
            if pattern.match(url):
                return False
        return True
    def load(self,pattern_file):
        if not self.use_url_whitelist:
            return
        if timeutils.utcnow_ts() - self.last_load < CONF.reload_url_filter_interval:
            return
        self.last_load = timeutils.utcnow_ts()
        self.patterns = set()
        if pattern_file and os.path.exists(pattern_file):
            handler = open(pattern_file, 'r')
            for pattern in handler:
                re_handler = re.compile("".join(pattern.split()))
                self.patterns.add(re_handler)
            handler.close()
        for pattern in self.url_whitelist:
            re_handler = re.compile("".join(pattern.split()))
            self.patterns.add(re_handler)


if __name__ == '__main__':
    filter = Filter(use_url_whitelist = True, url_whitelist = ['http://www.baidu.com/.*'])
    ret,reason = filter.filter('http://www.baidu.com/adsf')
    print ret, reason
    ret,reason = filter.filter('http://www.sina.com/adsf')
    print ret, reason
