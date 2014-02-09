'''
Created on 2014.1.28

@author: gaolichuang


use sqlalchemy as database backend
'''
import mmh3 # https://github.com/gaolichuang/mmh3

from eventlet import greenthread
from sqlalchemy import or_

from oslo.config import cfg
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging
from miracle.common.utils import timeutils
from miracle.common.db.sqlalchemy import utils as db_utils
from miracle.common.db.sqlalchemy import session as db_session
from cccrawler.proto import crawldoc
from cccrawler.proto.db import models
from miracle.common.db import utils
from cccrawler.handler import deweight
from cccrawler.utils import urlutils


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

def model_query(model, *args, **kwargs):
    """Query helper that accounts for context's `read_deleted` field.

    :param use_slave: If true, use slave_connection
    :param session: if present, the session to use
    """

    use_slave = kwargs.get('use_slave') or False
    if CONF.database.slave_connection == '':
        use_slave = False

    session = kwargs.get('session') or db_session.get_session(slave_session=use_slave)


    query = session.query(model, *args)
    return query

def __getCrawldoc(filters=None, sort_key=None, sort_dir='asc', limit=None):
    '''discard because Inefficiency'''
    filters = filters or {}

    # FIXME(sirp): now that we have the `disabled` field for instance-types, we
    # should probably remove the use of `deleted` to mark inactive. `deleted`
    # should mean truly deleted, e.g. we can safely purge the record out of the
    # database.

    query = model_query(models)

    if 'max_level' in filters:
        query = query.filter(
                models.CrawlPending.level <= filters['max_level'])

    query = db_utils.paginate_query(query, models.CrawlPending, limit,
                                           [sort_key, 'id'],
                                           marker=None, sort_dir=sort_dir)

    docs = query.all()

    return [_format_pending_crawldoc(doc) for doc in docs]

def _format_crawldoc(doc):
    '''TODO: add logic'''
    return crawldoc.CrawlDoc()

def _format_pending_crawldoc(doc):
    cdoc = crawldoc.CrawlDoc()
    cdoc.request_url = doc.request_url
    cdoc.url = doc.url
    cdoc.docid = doc.docid
    cdoc.reservation_dict = eval(doc.reservation_dict)
    cdoc.parent_url = doc.parent_docid
    cdoc.level = doc.level
    cdoc.detect_time = doc.detect_time
    cdoc.pending_id = doc.id
    return cdoc

def addPendingCrawlDoc(url, level, parent_id, res_dict = {},text = ''):
    pvalues = addPendingCrawlDocDict(url, level, parent_id, res_dict,text)
    pend_ref = models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save()
def addPendingCrawlDocDict(url, level, parent_id, res_dict = {},text = ''):
    pvalues = {}
    pvalues['request_url'] = url
    # fill url and docid when save to db
    pvalues['url'] = urlutils.normalize(url)
    pvalues['docid'] = mmh3.hash(pvalues['url'])
    pvalues['outlink_text'] = text
    pvalues['level'] = level + 1
    pvalues['reservation_dict'] = str(res_dict)
    pvalues['detect_time'] = int(timeutils.utcnow_ts())
    pvalues['crawl_status'] = 'fresh'
    pvalues['parent_docid'] = parent_id
    pvalues['recrawl_times'] = 0
    return pvalues
    pend_ref = models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save()
def rushPendingCrawlDoc(docs = []):
    if len(docs) == 0:
        return
    session = db_session.get_session()
    with session.begin():
        session.execute(
                models.CrawlPending.__table__.insert(),
                docs)
def saveSuccessCrawlDoc(crawldoc):
    '''step1: save crawl success crawldoc to crawl_result, make sure docid is unique
       step2: save outlinks(found new url) to crawl_pending
       step3: update crawl url status which at crawl_pending to crawled'''
    values = crawldoc.convert()
    values['reservation_dict'] = str(crawldoc.reservation_dict)
    values['created_at'] = timeutils.utcnow_ts()
    utils.convert_datetimes(values, 'created_at', 'deleted_at', 'updated_at')
    crawldoc_ref = models.CrawlResult()
    crawldoc_ref.update(values)
    crawldoc_ref.save()
    _updateCrawlStatus(crawldoc.pending_id,'crawled',crawlfail=False)
    cl = deweight.get_client()
    fresh_docs = []
    for doc in crawldoc.outlinks:
#        addPendingCrawlDoc(doc.url, crawldoc.level + 1,  crawldoc.docid, crawldoc.reservation_dict,doc.text,)
        if not cl.has(crawldoc.docid):
            fresh_doc = addPendingCrawlDocDict(doc.url, crawldoc.level + 1,  crawldoc.docid, crawldoc.reservation_dict,doc.text,)
            fresh_docs.append(fresh_doc)
    rushPendingCrawlDoc(fresh_docs)
def saveFailCrawlDoc(crawldoc):
    '''step1: save crawl fail crawldoc to crawl_fail_result, docid can repeat
       step2: update crawl url status which at crawl_pending to crawled
       step3: update or insert crawl fail status which at crawl_fail_pending'''
    values = crawldoc.convert()
    values['reservation_dict'] = str(crawldoc.reservation_dict)
    values['created_at'] = timeutils.utcnow_ts()
    utils.convert_datetimes(values, 'created_at', 'deleted_at', 'updated_at')
    crawldoc_ref = models.CrawlFailResult()
    crawldoc_ref.update(values)
    crawldoc_ref.save()
    _updateCrawlStatus(crawldoc.pending_id,'crawled',crawlfail=False)
    
    pvalues = {}
    pvalues['request_url'] = crawldoc.request_url
    pvalues['reservation_dict'] = str(crawldoc.reservation_dict)
    pvalues['level'] = crawldoc.level
    pvalues['detect_time'] = crawldoc.detect_time
    pvalues['crawl_status'] = 'fresh'
    pvalues['parent_docid'] = crawldoc.parent_docid
    pvalues['recrawl_times'] = 0
    pend_ref = models.CrawlFailPending()
    pend_ref.update(pvalues)
    pend_ref.save()

def getFreshCrawlDoc(limit,level):
    '''param limit: want get how many crawldocs
        step1: get limit crawldoc from crawl_pending 
        step2: mark crawlstatus to crawl_status update recrawltimes and schedule time'''
    filters = {'crawl_status':'fresh',
               'max_level':level}
    docs = _getPendingCrawldoc(filters = filters, limit = limit, sort_key = 'level')
    LOG.debug(_("get Fresh Crawldoc number %(docs)s"),{'docs':len(docs)})
    for doc in docs:
        _updateScheduleDoc(doc.id, doc.recrawl_times, 'crawled', crawlfail = False)
    return [_format_pending_crawldoc(doc) for doc in docs]

def getTimeoutCrawlDoc(timeout, max_timeout_time, limit):
    ''' param timeout: compare with schedule time at crawl_pending to detect timeout crawldoc
        param max_timeout_time: compare with recrawl_times to decide get or not
        step1: get status is schedule and timeout doc
        setp2: update crawl_pending recrawl_times and schedule_time'''
    filters = {'crawl_status':'scheduled',
               'max_recrawl_time':max_timeout_time,
               'timeout':timeout}
    docs = _getPendingCrawldoc(filters = filters, limit = limit)
    LOG.debug(_("get Timeout Crawldoc number %(docs)s"),{'docs':len(docs)})
    for doc in docs:
        _updateScheduleDoc(doc.id,doc.recrawl_times,'scheduled',crawlfail = False)
    return [_format_pending_crawldoc(doc) for doc in docs]

def getFailCrawlDoc(retry_time,limit):
    ''' param retry_time: get fail doc from crawl_fail_pending which recrawl_times less then retry_time
        step 1: get doc from crawl_fail_pending which status is crawled or NULL and recrawl_times < retry_time
        step 2: update recrawltime and crawlstatus and schedule time'''
    filters = {'crawl_status':'fresh',
               'max_recrawl_time':retry_time}
    docs = _getPendingCrawldoc(crawlfail = True, filters = filters, limit = limit)
    LOG.debug(_("get Fail Crawldoc number %(docs)s"),{'docs':len(docs)})
    for doc in docs:
        _updateScheduleDoc(doc.id,doc.recrawl_times,'crawled',crawlfail = True)
    return [_format_pending_crawldoc(doc) for doc in docs]

def getTimeoutFailCrawlDoc(timeout, max_timeout_time,limit):
    filters = {'crawl_status':'scheduled',
               'max_recrawl_time':max_timeout_time,
               'timeout':timeout}
    docs = _getPendingCrawldoc(crawlfail = True, filters = filters, limit = limit)
    LOG.debug(_("get Fail Timeout Crawldoc number %(docs)s"),{'docs':len(docs)})
    for doc in docs:
        _updateScheduleDoc(doc.id,doc.recrawl_times,'scheduled',crawlfail = True)
    return [_format_pending_crawldoc(doc) for doc in docs]    

def _updateScheduleDoc(pend_id, recrawl_time,crawl_status, crawlfail = False):
    pvalues = {}
    pvalues['id'] = pend_id
    pvalues['crawl_status'] = crawl_status
    pvalues['schedule_time'] = int(timeutils.utcnow_ts())
    pvalues['recrawl_times'] = recrawl_time + 1
    if crawlfail:
        pend_ref = models.CrawlFailPending()
    else:
        pend_ref= models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save(update = True)
def _updateCrawlStatus(pend_id, crawl_status, crawlfail = False):
    pvalues = {}
    pvalues['id'] = pend_id
    pvalues['crawl_status'] = crawl_status
    if crawlfail:
        pend_ref = models.CrawlFailPending()
    else:
        pend_ref= models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save(update = True)

def _updateScheduleTime(pend_id, crawlfail = False):
    pvalues = {}
    pvalues['id'] = pend_id
    pvalues['schedule_time'] = int(timeutils.utcnow_ts())
    if crawlfail:
        pend_ref = models.CrawlFailPending()
    else:
        pend_ref= models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save(update = True)
    
def _addRecrawlTime(pend_id,recrawl_time, crawlfail = False):
    pvalues = {}
    pvalues['id'] = pend_id
    pvalues['recrawl_times'] = recrawl_time + 1
    if crawlfail:
        pend_ref = models.CrawlFailPending()
    else:
        pend_ref= models.CrawlPending()
    pend_ref.update(pvalues)
    pend_ref.save(update = True)    
    
    
def _getPendingCrawldoc(crawlfail = False, delete = False, filters=None,
                       limit=None, sort_key=None, sort_dir='asc'):
    filters = filters or {}

    # FIXME(sirp): now that we have the `disabled` field for instance-types, we
    # should probably remove the use of `deleted` to mark inactive. `deleted`
    # should mean truly deleted, e.g. we can safely purge the record out of the
    # database.

    if crawlfail:
        models_table = models.CrawlFailPending
    else:
        models_table = models.CrawlPending
    query = model_query(models_table)
    if 'crawl_status' in filters and filters['crawl_status'] == 'fresh':
        query = query.filter(or_(models_table.crawl_status == 'fresh',
                                 models_table.crawl_status == ''))
    if 'crawl_status' in filters and filters['crawl_status'] == 'scheduled':
        query = query.filter(models_table.crawl_status == 'scheduled')

    if 'max_level' in filters:
        query = query.filter(models_table.level <= filters['max_level'])

    if 'max_recrawl_time' in filters:
        query = query.filter(
                models_table.recrawl_times <= filters['max_recrawl_time'])    
    if 'timeout' in filters:
        query = query.filter(
                models_table.schedule_time <= filters['timeout'])
    LOG.debug(_("get crawldoc sql %(query)s"),{'query':query})
    
    return query.all()

def getAllDocId():
    '''get all docid from crawlpending use for de weight'''
    session = db_session.get_session()
    with session.begin():
        keys = session.execute('select docid from crawl_pending').fetchall()                                                                   
    return keys

if __name__ == '__main__':
    pass
