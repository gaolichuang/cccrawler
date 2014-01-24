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


from cccrawer.thirdparty.BeautifulSoup import BeautifulSoup # For processing HTML
from cccrawer.thirdparty.BeautifulSoup import BeautifulStoneSoup # For processing XML

parser_opts = [
    cfg.ListOpt('interest_tags',
               default=[],
               help='interest tags'),
    cfg.BoolOpt('no_follow',
                default=False,
                help = 'extract no follow link or not'),
    cfg.BoolOpt('extract_inlink',
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
        self.times = []  # [("item", starttime, endtime), ...]
        
    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    def process(self,crawldoc):
        start_time = time.time()

        # assign self vars
        for name,value in vars(self).items():
            if not name.startswith('__'):
                if  isinstance(value, (list,dict)):
                    self.__dict__[name] = copy.copy(getattr(crawldoc, name))
                else:
                    self.__dict__[name] = getattr(crawldoc, name)
        LOG.debug(_("Begin Parse Crawldoc: %(crawldoc)s"),{'crawldoc':crawldoc})
        LOG.debug(_("Begin Parse Parser: %(Parser)s"),{'Parser':self})
        self.parse()
        LOG.debug(_("After Parse Parser: %(Parser)s"),{'Parser':self})
        for name,value in vars(self).items():
            if not name.startswith('__'):
                if  isinstance(value, (list,dict)):
                    crawldoc.__dict__[name] = copy.copy(getattr(self, name))
                else:
                    crawldoc.__dict__[name] = getattr(self, name)
        LOG.debug(_("After Parse Crawldoc: %(crawldoc)s"),{'crawldoc':crawldoc})
        self.times.append(("%s" % crawldoc.url,
                           start_time, time.time()))
    def parse(self):
        raise NotImplementedError
    def __str__(self):
        return utils.ToStr(self)




class SoupHtmlParser(HtmlParser):
    '''use BeautifulSoup to parse html'''
    def __init__(self):
        super(SoupHtmlParser,self).__init__()
    def parse(self):
        pass




_IMPL_HTMLPARSER_ = 'cccrawler.handler.htmlparser.SoupHtmlParser'
def get_parser_class():
    return utils.import_class(_IMPL_HTMLPARSER_)
def Parser(*args, **kwargs):
    parser_class = get_parser_class()
    return parser_class(*args, **kwargs)

