'''
Created on 2014.1.28

@author: gaolichuang
'''
from sqlalchemy import Column, Index, Integer, BigInteger, Enum, String, schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
#from sqlalchemy.orm import relationship, backref, object_mapper

from miracle.common.db.sqlalchemy import models

# this must be here!!! use this to create tables
BASE = declarative_base()

class CrawlResultBase(object):
    id = Column('id', Integer, primary_key=True)
    request_url = Column('request_url', String(255))
    detect_time =  Column('detect_time', Integer)
    reservation_dict = Column('reservation_dict', Text)  # this is dict
    parent_url = Column('parent_url',String(255))
    level = Column('level',String(255))
    url = Column('url', String(255))
    docid = Column('docid', Integer)

    host = Column('host',String(64))
    fake_host = Column('fake_host',String(64))
    method = Column('method',String(10))
    referer = Column('referer',String(255))
    custom_accept_types = Column('custom_accept_types',String(255))
    code =  Column('code', Integer)
    reason = Column('reason',String(255))
    history = Column('history', Text)  # this is list
    header = Column('header', Text) # this is dict translate: dict to str
    content = Column('content', Text)
    content_type = Column('content_type',String(255))
    redirect_url = Column('redirect_url',String(255))
    crawl_time =  Column('crawl_time', Integer)
    orig_encoding = Column('orig_encoding',String(255))
    conv_encoding = Column('conv_encoding',String(255))


class CrawlResult(BASE,models.ModelBase,CrawlResultBase):
    '''
    Desc: use to save crawl result.
        include all field of crawldoc except outlinks, only crawl success doc save here
        dict and list save to Text
    di = {'aa': 'aaaaa', 'bb': 11}
    dict to string:
        sdi = str(di)
    string to dict:
        ddi = eval(sdi)
    li = ['aa','bb','sdfew']
    list to string:
        sli = str(li)
    string to list:
        lli = eval(sli)
    '''
    __tablename__ = 'crawl_result'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

class CrawlFailResult(BASE,models.ModelBase,CrawlResultBase):
    '''it allow not only one url record,
        it has create time and update time, fill at handler'''
    __tablename__ = 'crawl_fail_result'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

class CrawlPendingBase(object):
    id = Column('id', Integer, primary_key=True)  # this will carry at crawldoc
    request_url = Column('request_url', String(255))
    
    # url and docid id calculated by request_url
    url = Column('url', Integer)
    docid = Column('docid', Integer)

    outlink_text = Column('outlink_text', Text) # outlink text
    reservation_dict = Column('reservation_dict', Text)  # type dict
    parent_docid = Column('parent_docid',Integer)
    level = Column('level',String(255))
    detect_time = Column('detect_time', Integer) # maybe same with create_time,but it is timestamp
    schedule_time = Column('schedule_time', Integer)  # timestamp use for timeout
    recrawl_times = Column('recrawl_times', Integer)  # recrawl time
    # crawl status: fresh or None(find) scheduled(find and schedule out) crawled(finish crawl)
    # finish crawl maybe soft delete
    crawl_status =  Column('crawl_status', String(32))


class CrawlPending(BASE, models.MixinModelBase,CrawlPendingBase):
    '''save the url which already found but not crawl
        save crawl success extract outlinks
        CrawlPending has all urls, it could to be use for derepeat, use docid'''
    __tablename__ = 'crawl_pending'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

class CrawlFailPending(BASE, models.MixinModelBase,CrawlPendingBase):
    '''save the crawl fail url, use to recrawl'''
    __tablename__ = 'crawl_fail_pending'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
