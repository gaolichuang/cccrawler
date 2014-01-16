'''
Created on 2014.1.8

@author: gaolichuang
'''

from eventlet import greenthread
from miracle.common.manager import manager as base_manager
from miracle.common.manager import periodic_task
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging
from oslo.config import cfg

CONF = cfg.CONF
CONF.import_opt('max_queue_size', 'miracle.common.service.multiservice')
LOG = logging.getLogger(__name__)

class CrawlManager(base_manager.Manager):
    def __init__(self):
        super(CrawlManager,self).__init__()
        self._m_input_queue = None
        self._m_output_queue = None
    @property
    def m_input_queue(self):
        return self._m_input_queue
    @m_input_queue.setter
    def m_input_queue(self,queue):
        self._m_input_queue = queue
    @property
    def m_output_queue(self):
        return self._m_output_queue
    '''Attention: this property must unique'''
    @m_output_queue.setter
    def m_output_queue(self,queue):
        self._m_output_queue = queue

    def run_periodic_report_tasks(self,service):
        LOG.info(_(" Periodic report task at %(cname)s id:%(m_id)s"),
                    {'cname':self.__class__.__name__, 'm_id':self.m_id})

    def ProcessCrawlDoc(self,crawldoc):
        pass

    def output(self,crawldoc):
        self.wait_for_outputqueue_ready()
        try:
            self._m_output_queue.put(crawldoc)
            LOG.debug(_(" Output One Crawldoc at %(cname)s mid:%(m_id)s, \nCrawlDoc:\n%(doc)s"),
                        {'cname':self.__class__.__name__, 'm_id':self.m_id,'doc':crawldoc})
        except AttributeError:
            LOG.debug(_(" Output queue is None at %(cname)s mid:%(m_id)s"),{'cname':self.__class__.__name__, 'm_id':self.m_id})

    def Run(self, context, *args, **kwargs):
        LOG.info(_(" %(cname)s id:%(m_id)s Start to Run, InputQueue %(input_q)s, OutputQueue %(output_q)s"),
                    {'cname':self.__class__.__name__, 'm_id':self.m_id,
                    'input_q':self._m_input_queue,'output_q':self._m_output_queue})
        while True:
            if self._m_input_queue == None:
                LOG.debug(_("Manager %(cname)s inputqueue is None"),{'cname':self.__class__.__name__})
                break
            if self._m_input_queue.empty():
#                LOG.debug(_("Manager %(cname)s mid:%(m_id)s inputqueue is Empty"),
#                            {'cname':self.__class__.__name__, 'm_id':self.m_id})
                greenthread.sleep(3)
                continue
            crawldoc = self._m_input_queue.get()
            LOG.debug(_(" Get Crawldoc at %(cname)s mid:%(m_id)s, \nCrawlDoc:\n%(doc)s"),
                        {'cname':self.__class__.__name__, 'm_id':self.m_id,'doc':crawldoc})
            self.ProcessCrawlDoc(crawldoc)
            self.output(crawldoc)

    def wait_for_outputqueue_ready(self):
        while True:
            if self._m_output_queue == None or \
                    self._m_output_queue.qsize() < CONF.max_queue_size:
                break
            else:
                greenthread.sleep(3)
                LOG.debug(_(" Output Queue is Full at %(cname)s mid:%(m_id)s"),
                            {'cname':self.__class__.__name__, 'm_id':self.m_id})

    def wait_for_inputqueue_ready(self):
        while True:
            if self._m_output_queue == None or \
                    self._m_input_queue.qsize() < CONF.max_queue_size:
                break
            else:
                greenthread.sleep(3)
                LOG.debug(_(" Input Queue is Full at %(cname)s mid:%(m_id)s"),
                            {'cname':self.__class__.__name__, 'm_id':self.m_id})
