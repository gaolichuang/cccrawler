import sys

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
        if name.startswith('__'):
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
    return str(sorted(r_dict.items(),key=lambda e:e[1],reverse=reverse))
