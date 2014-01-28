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


class CrawlResult(BASE,models.ModelBase):
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
    id = Column('id', Integer, primary_key=True)
    request_url = Column('request_url', String(255))
    detect_time =  Column('d_time', Integer)
    reservation_dict = Column('res', Text)  # this is dict
    parent_url = Column('p_url',String(255))
    level = Column('level',String(255))
    url = Column('url', String(255))
    docid = Column('docid', Integer)

    host = Column('host',String(64))
    fake_host = Column('fkhost',String(64))
    method = Column('method',String(10))
    referer = Column('referer',String(255))
    custom_accept_types = Column('custom_a_t',String(255))
    code =  Column('code', Integer)
    reason = Column('reason',String(255))
    history = Column('history', Text)  # this is list
    header = Column('header', Text) # this is dict translate: dict to str
    content = Column('content', Text)
    content_type = Column('content_t',String(255))
    redirect_url = Column('r_url',String(255))
    crawl_time =  Column('c_time', Integer)
    orig_encoding = Column('o_encoding',String(255))
    conv_encoding = Column('c_encoding',String(255))


class CrawlFailResult(CrawlResult,models.TimestampMixin):
    '''it allow not only one url record,
        it has create time and update time, fill at handler'''
    __tablename__ = 'crawl_fail_result'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

class CrawlPending(BASE, models.MixinModelBase):
    '''save the url which already found but not crawl
        save crawl success extract outlinks'''
    __tablename__ = 'crawl_pending'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column('id', Integer, primary_key=True)  # this will carry at crawldoc
    request_url = Column('request_url', String(255))
    outlink_text = Column('content', Text) # outlink text
    reservation_dict = Column('res', Text)  # type dict
    parent_docid = Column('p_id',Integer)
    level = Column('level',String(255))
    detect_time = Column('d_time', Integer) # maybe same with create_time,but it is timestamp
    schedule_time = Column('s_time', Integer)  # timestamp use for timeout
    recrawl_times = Column('r_times', Integer)  # recrawl time
    # crawl status: fresh or None(find) scheduled(find and schedule out) crawled(finish crawl)
    # finish crawl maybe soft delete
    crawl_status =  Column('c_status', String(32))
    

class CrawlFailPending(CrawlPending):
    '''save the crawl fail url, use to recrawl'''
    __tablename__ = 'crawl_fail_pending'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    