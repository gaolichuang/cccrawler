'''
Created on 2014.1.22

@author: gaolichuang
'''

import sys

from oslo.config import cfg

from miracle.common import config
from miracle.common.base import log as logging
from miracle.common.service import service
from miracle.common.service import multiservicechain

def main():
    config.parse_args(sys.argv)
    logging.setup("cccrawler")

    server = multiservicechain.MultiServer.create(
                    managers = ['cccrawler.scheduler.manager.DummySchedulerManager',
                                'cccrawler.fetcher.managercontainer.FetcherManagerContainer',
                                'cccrawler.handler.manager.HandlerManager'])

    service.serve(server)
    service.wait()


if __name__ == '__main__':
    import sys 
    reload(sys)
    sys.setdefaultencoding('utf-8') 
    main()

