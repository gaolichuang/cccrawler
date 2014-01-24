'''
Created on 2014.1.19

@author: gaolichuang@gmail.com
'''
import time
import copy

from oslo.config import cfg
from cccrawler import utils
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

fetch_client_opts = [
    cfg.StrOpt('user_agent',
               default='cccrawler-spider',
               help='user_agent'),
    cfg.ListOpt('accept_types',
               default = ['text/html','application/xhtml+xml','application/xml;q=0.9,image/webp,*/*;q=0.8'],
               help='request accept types'),
    cfg.BoolOpt('http_debug',
                default=False,
                help = 'http debug mode or not'),
    cfg.IntOpt('http_time_out',
               default = 5,
               help = 'default time out for http connection')
]

CONF = cfg.CONF
CONF.register_opts(fetch_client_opts)
LOG = logging.getLogger(__name__)

class Request(object):
    def __init__(self, url = None, method = 'GET', referer = None):
        self.url = url
        self.method = method
        self.referer = referer
    def FillByCrawlDoc(self, crawldoc):
        for name,value in vars(self).items():
            if not name.startswith('__'):
                if  isinstance(value, (list,dict)):
                    self.__dict__[name] = copy.copy(getattr(crawldoc, name))
                else:
                    self.__dict__[name] = getattr(crawldoc, name)

    def __str__(self):
        return utils.ToStr(self)
class Response(object):
    def __init__(self):
        self.code = -1
        self.reason = None
        self.history = []  # redirect history
        self.header = {}
        self.content = ''
        self.content_type = None # get from http header like text/html
        self.redirect_url = None
        # get from analysis from content
        self.orig_encoding = None   # get from the metadata
        self.conv_encoding = 'utf-8'
    def FillCrawlDoc(self, crawldoc):
        for name,value in vars(self).items():
            if not name.startswith('__'):
                if  isinstance(value, (list,dict)):
                    crawldoc.__dict__[name] = copy.copy(getattr(self, name))
                else:
                    crawldoc.__dict__[name] = getattr(self, name)

    def __str__(self):
        return utils.ToStr(self)


class HttpClient(object):
    def __init__(self, timeout = None, http_log_debug = None,
                  user_agent = None, accept_types = None):
        self.timeout = timeout
        self.user_agent = user_agent
        self.accept_types = accept_types
        self.http_log_debug = CONF.http_debug
        if self.timeout == None:
            self.timeout = CONF.http_time_out
        if self.user_agent == None:
            self.user_agent = CONF.user_agent
        if self.accept_types == None:
            self.accept_types = CONF.accept_types
        self.times = []  # [("item", starttime, endtime), ...]
        
    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    def http_log_req(self, method, url, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']

        if not kwargs.get('verify', True):
            string_parts.append(' --insecure')

        string_parts.append(" '%s'" % url)
        string_parts.append(' -X %s' % method)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        if 'data' in kwargs:
            string_parts.append(" -d '%s'" % (kwargs['data']))
        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        self._logger.debug(
            "RESP: [%s] %s\nRESP BODY: %s\n",
            resp.status_code,
            resp.headers,
            resp.text)

    def process(self,crawldoc):
        start_time = time.time()
        request = Request()
        request.FillByCrawlDoc(crawldoc)
        LOG.debug(_("Begin Fetch Crawldoc: %(crawldoc)s"),{'crawldoc':crawldoc})
        LOG.debug(_("Begin Fetch Request: %(request)s"),{'request':request})
        response = self.fetch(request)
        LOG.debug(_("Finish Fetch Response: %(response)s"),{'response':response})
        response.FillCrawlDoc(crawldoc)
        LOG.debug(_("Finish Fetch Crawldoc: %(Crawldoc)s using:%(usetime)ss"),
                    {'Crawldoc':crawldoc,'usetime':(time.time()-start_time)})
        self.times.append(("%s %s" % (request.method, request.url),
                           start_time, time.time()))
    
    def fetch(self,request):
        raise NotImplementedError



_IMPL_HTTPCLIENT_ = 'cccrawler.fetcher.requestclient.HTTPClient'
def get_client_class():
    return utils.import_class(_IMPL_HTTPCLIENT_)
def Client(*args, **kwargs):
    client_class = get_client_class()
    return client_class(*args, **kwargs)

