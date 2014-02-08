'''
Created on 2014.2.8

@author: gaolichuang@gmail.com
'''

from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging

LOG = logging.getLogger(__name__)


_crawldoc_healthy_level = ['Normal','Warning','Fatal']
class CrawlDocChecker(object):
    ''' use at scheduler send url out'''
    def __init__(self):
        pass
    def checkbefore(self,crawldoc):
        level,reason = self.getLevelbefore(crawldoc)
        if level > 0:
            LOG.info(_('CrawlDoc Check before Healthy: %(level)s Reason:%(reason)s,CrawlDoc:\n%(doc)s'),
                     {'level':_crawldoc_healthy_level[level],
                      'reason':reason,
                      'doc':crawldoc})
        else:
            LOG.debug(_('CrawlDoc Check before Healthy: %(level)s Reason:%(reason)s'),
                     {'level':_crawldoc_healthy_level[level],
                      'reason':reason,
                      'doc':crawldoc})
        if level == 2:
            return False
        return True
    def getLevelbefore(self,crawldoc):
        level = 0
        reason = 'Healthy'
        if crawldoc.request_url == None or crawldoc.request_url == '':
            return 2,'Not Set request_url'
        if crawldoc.url == None or crawldoc.url == '':
            return 2,'Not Set url'
        if crawldoc.url == None or crawldoc.url == '':
            return 2,'Not Set url'
        if crawldoc.docid == None:
            return 2,'Not Set docid'        
        return level,reason

    def checkafter(self,crawldoc):
        level,reason = self.getLevelAfter(crawldoc)
        if level > 0:
            LOG.info(_('CrawlDoc Check After Healthy: %(level)s Reason:%(reason)s,CrawlDoc:\n%(doc)s'),
                     {'level':_crawldoc_healthy_level[level],
                      'reason':reason,
                      'doc':crawldoc})
        else:
            LOG.debug(_('CrawlDoc Check After Healthy: %(level)s Reason:%(reason)s'),
                     {'level':_crawldoc_healthy_level[level],
                      'reason':reason,
                      'doc':crawldoc})
        if level == 2:
            return False
        return True

    def getLevelAfter(self, crawldoc):
        level,reason = self.getLevelbefore(crawldoc)
        if level == 2:
            return level,reason
        reasons = []
        if crawldoc.code == None:
            reasons.append('No code')
            level = 2
            return level,'#'.join(reasons)

        if crawldoc.content == '':
            reasons.append('No Content')
            level = 1
        elif len(crawldoc.content) < 128:
            reasons.append('Content Too Little')
            level = 1

        if crawldoc.crawl_time == None or crawldoc.crawl_time == 0:
            reasons.append('crawl_time not fill')
            level = 1
        if len(crawldoc.outlinks) == 0:
            reasons.append('outlinks not fill')
            level = 1
        return level,'#'.join(reasons)
if __name__ == '__main__':
    pass