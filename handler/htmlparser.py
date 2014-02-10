'''
Created on 2014.1.19

@author: gaolichuang@gmail.com
'''
import time
import copy
import urlparse

from oslo.config import cfg
from cccrawler import utils
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging 


from cccrawler.thirdparty.BeautifulSoup import BeautifulSoup # For processing HTML
from cccrawler.thirdparty.BeautifulSoup import BeautifulStoneSoup # For processing XML
from cccrawler.handler import urlfilter
from cccrawler.utils import urlutils
from cccrawler.proto.crawldoc import OutLink

parser_opts = [
    cfg.BoolOpt('filter_no_follow',
                default=False,
                help = 'extract no follow link or not'),
    cfg.BoolOpt('filter_onclick',
                default=False,
                help = 'extract no follow link or not'),
    cfg.BoolOpt('extract_indomain_link',
                default=True,
                help = 'extract the same domain links'),
]

CONF = cfg.CONF
CONF.register_opts(parser_opts)
LOG = logging.getLogger(__name__)

class HtmlParser(object):
    def __init__(self):
        self.content = None
        self.url = None
        self.outlinks = []
        self.__times = []  # [("item", starttime, endtime), ...]
        
    def get_timings(self):
        return self.__times

    def reset_timings(self):
        self.__times = []

    def process(self,crawldoc):
        start_time = time.time()
        # only text/html and text/xml need parse outlinks
        content_type = crawldoc.header.get('Content-Type','text')
        if content_type.find('text') == -1:
            LOG.debug(_("No need to Parse: %(crawldoc)s"),{'crawldoc':crawldoc})
            return
        # assign self vars
        for name,value in vars(self).items():
            if not name.startswith('_'):
                if  isinstance(value, (list,dict)):
                    self.__dict__[name] = copy.copy(getattr(crawldoc, name))
                else:
                    self.__dict__[name] = getattr(crawldoc, name)
        LOG.debug(_("Begin Parse Crawldoc: %(crawldoc)s"),{'crawldoc':crawldoc})
        LOG.debug(_("Begin Parse: %(Parser)s"),{'Parser':self})
        self.outlinks = []
        self.parse()
        LOG.debug(_("After Parse Parser: %(Parser)s"),{'Parser':self})
        for name,value in vars(self).items():
            if not name.startswith('_'):
                if  isinstance(value, (list,dict)):
                    crawldoc.__dict__[name] = copy.copy(getattr(self, name))
                else:
                    crawldoc.__dict__[name] = getattr(self, name)
        LOG.debug(_("After Parse Crawldoc: %(crawldoc)s, use: %(stime)s"),
                    {'crawldoc':crawldoc,'stime':time.time() - start_time})
        self.__times.append(("%s" % crawldoc.url,
                           start_time, time.time()))
    def parse(self):
        raise NotImplementedError
    def __str__(self):
        return utils.ToStr(self)

class SoupHtmlParser(HtmlParser):
    '''use BeautifulSoup to parse html'''
    def __init__(self):
        super(SoupHtmlParser,self).__init__()
        self.__filter = urlfilter.Filter()
    def parse(self):
        url_dict = {}
        url_parse = urlparse.urlparse(self.url)
        base_url = urlparse.ParseResult(url_parse.scheme,url_parse.netloc,'/',None,None,None).geturl()
        base_url_domain = urlutils.getdomain(self.url)
        LOG.info(_("Url: %(url)s,Get BaseUrl: %(baseurl)s and base_domain:%(basedomain)s"),
                          {'url':self.url,'baseurl':base_url,'basedomain':base_url_domain})

        soup = BeautifulSoup(self.content)
        for a_tag in soup.findAll('a'):
            if not a_tag.has_key('href'):
                continue
            if a_tag['href'].lower().find('javascript') != -1:
                continue
            if CONF.filter_no_follow and a_tag.has_key('nofollow'):
                continue
            if CONF.filter_onclick and a_tag.has_key('onclick'):
                continue

            new_url = a_tag['href']
            if base_url and not new_url.startswith("http"):
                if new_url.startswith('/'):
                    new_url = new_url[1:]
                new_url = base_url + new_url
            ret,reason =  self.__filter.filter(new_url)
            if ret:
                LOG.info(_("Filter Url: %(url)s,Reason: %(reason)s"),
                          {'url':new_url,'reason':reason})
                continue
            if CONF.extract_indomain_link:
                domain = urlutils.getdomain(new_url)
                if not domain.lower() == base_url_domain.lower():
                    LOG.info(_("Filter Url: %(url)s,Reason: NotInDomain"),
                          {'url':new_url})                    
                    continue
            if new_url in url_dict.keys():
                if not a_tag.string in url_dict[new_url]:
                    url_dict[new_url].append(a_tag.string)
                    LOG.debug(_("Add outlink Text Url: %(url)s,value: %(value)s"),
                                {'url':new_url,'value':url_dict[new_url]})
            else:
                l = list()
                l.append(a_tag.string)
                url_dict[new_url] = l
            LOG.debug(_("Extract Outlink: url: %(url)s,text: %(text)s "),
                        {'url':new_url,'text':a_tag.string})
        for key,value in url_dict.iteritems():
            ol = OutLink(url = key, text = '$@$'.join(value))
            self.outlinks.append(ol)

_IMPL_HTMLPARSER_ = 'cccrawler.handler.htmlparser.SoupHtmlParser'
def get_parser_class():
    return utils.import_class(_IMPL_HTMLPARSER_)
def Parser(*args, **kwargs):
    parser_class = get_parser_class()
    return parser_class(*args, **kwargs)

