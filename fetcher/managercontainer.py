'''
Created on 2014.1.1

@author: gaolichuang
'''
import random
from eventlet import queue
from eventlet import greenthread

from oslo.config import cfg
from miracle.common.manager.managercontainer import ManagerContainer
from miracle.common.base import log as logging
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.utils import importutils
from cccrawler.proto.crawldoc import CrawlDoc

container_fetcher_opts = [
    cfg.StrOpt('fetcher_manager',
               default='cccrawler.fetcher.manager.FetcherManager',
               help='fetcher manager name'),
    cfg.IntOpt('fetcher_number',
               default=10,
               help='fetcher manager number'),
]

CONF = cfg.CONF
CONF.register_opts(container_fetcher_opts)

from cccrawler.fetcher.dispatch import Dispatcher

LOG = logging.getLogger(__name__)

class FetcherManagerContainer(ManagerContainer):
    def __init__(self, manager = None):
        super(FetcherManagerContainer, self).__init__(manager)
        self._input_queue = None
        self._output_queue = None
        self.m_name = self.__class__.__name__
        self.fetcher_managers = []
        self.dispatcher = Dispatcher()
        LOG.info(_("=====================Start FetcherManager  number:%s===================="% CONF.fetcher_number))
        i = 0
        while i < CONF.fetcher_number:
            manager_class_name = importutils.import_class(CONF.fetcher_manager)
            manager_class = manager_class_name()
            self.fetcher_managers.append(manager_class)
            LOG.info(_("Start Manager: %(mname)s id:%(m_id)s"),
                        {'mname':manager_class.__class__.__name__,'m_id':manager_class.m_id})
            i += 1
        LOG.info(_(60*"="))
            
    def periodic_report_tasks(self, service, raise_on_error=False):
        '''fix interval task, you can rewrite run_periodic_report_tasks fuction'''
        try:
            for fetcher in self.fetcher_managers:
                fetcher.run_periodic_report_tasks(service)
        except Exception as e:
            if raise_on_error:
                raise
            LOG.exception(_("Error during %(full_task_name)s: %(e)s"), locals())

    def Run(self, context, *args, **kwargs):
        '''set up queue, start fetchers'''
        if self._input_queue == None:
            LOG.info(_("Manager %(cname)s inputqueue is None"),{'cname':self.__class__.__name__})
            raise
        for fetcher in self.fetcher_managers:
            fetcher.m_output_queue = self.output_queue
            fetcher.m_input_queue = queue.LightQueue(CONF.max_queue_size)
            context.tg.add_thread(fetcher.Run, context, *args, **kwargs)
        while True:
            if self._input_queue.empty():
                greenthread.sleep(3)
                continue
            crawldoc = self._input_queue.get()
            fetch_id = self.dispatcher.dispatch(crawldoc)
            print fetch_id
            print len(self.fetcher_managers)
            LOG.debug(_("Prepare dispatch to %(fetch_num)s , crawldoc: %(crawldoc)s"), 
                            {'fetch_num':self.fetcher_managers[fetch_id].m_id,
                             'crawldoc':crawldoc})
            '''TODO: One fetcher hang will hang dispatch, if queue full, try put the queue front
            element to queue end'''
            self.fetcher_managers[fetch_id].wait_for_inputqueue_ready()
            self.fetcher_managers[fetch_id].m_input_queue.put(crawldoc)


    def pre_start_hook(self,context):
        for manager in self.fetcher_managers:
            LOG.info(_("%(cname)s id:%(m_id)s Pre_start_hook"),{'cname':manager.__class__.__name__,'m_id':manager.m_id})
            manager.pre_start_hook()

    def post_start_hook(self,context):
        for manager in self.fetcher_managers:
            LOG.info(_("%(cname)s id:%(m_id)s Post_start_hook"),{'cname':manager.__class__.__name__,'m_id':manager.m_id})
            manager.post_start_hook()
        ''' start multi fetchers'''
        if context.periodic_enable:
            if context.periodic_fuzzy_delay:
                initial_delay = random.randint(0, context.periodic_fuzzy_delay)
            else:
                initial_delay = None
                for fetcher in self.fetcher_managers:
                    ''' start periodic tasks'''
                    context.tg.add_dynamic_timer(fetcher.run_periodic_tasks,
                                     initial_delay=initial_delay,
                                     periodic_interval_max=
                                        context.periodic_interval_max,
                                     context = context)
