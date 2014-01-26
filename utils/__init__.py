
import sys
import os
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as logging 

LOG = logging.getLogger(__name__)

def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)


def ToDict(obj):
    '''use for serialize to dict'''
    raw_dict = {}
    for name,value in vars(obj).items():
#            print('%s=%s'%(name,value))
        if name.startswith('_'):
            continue
        if  isinstance(value, list):
            raw = []
            for ol in value:
                try:
                    raw.append(ol.convert)
                except:
                    raw.append(ol)
            raw_dict[name] = raw
        elif isinstance(value, dict):
            raw = {}
            for k in value.keys():
                try:
                    raw[k] = value[k].convert
                except:
                    raw[k] = value[k]
            raw_dict[name] = raw
        else:
            try:
                raw_dict[name] = value.convert
            except:
                raw_dict[name] = value
    return raw_dict

def ToStr(obj, clean_content = True, reverse = True):
    r_dict = ToDict(obj)
    if clean_content:
        r_dict['content'] = ''
        pass
    return str(sorted(r_dict.items(),key=lambda e:e[1],reverse=reverse))


def loadConfToDict(load_dict, conf_list, conf_file, conf_str = ''):
    '''params:'''
    LOG.debug(_("%(confstr)s Load from list: %(clist)s, file: %(cfile)s "),
                {'confstr':conf_str,'clist':conf_list,'cfile':conf_file})
    for line in conf_list:
        info = line.split(',')
        info[0] = "".join(info[0].split())
        if not info[0] in load_dict.keys():
            load_dict[info[0]] = info[1]
            LOG.debug(_("%(confstr)s Load key: %(info0)s, value:%(info1)s"),
                        {'confstr':conf_str,'info0':info[0],'info1':info[1]})
    if conf_file and os.path.exists(conf_file):
        fp = open(conf_file, 'r')
        lines = fp.readlines()
        for line in lines:
            info = line.split(',')
            info[0] = "".join(info[0].split())
            if not info[0] in load_dict.keys():
                load_dict[info[0]] = info[1]
                LOG.debug(_("%(confstr)s Load from file key: %(info0)s, value:%(info1)s"),
                            {'confstr':conf_str,'info0':info[0],'info1':info[1]})
        fp.close()
    else:
        LOG.debug(_("%(confstr)s conf file not exist conf file:%(cfile)s"),
                    {'confstr':conf_str,'clist':conf_list,'cfile':conf_file})
