# -*- coding: UTF-8 -*- 
'''
Created on 2014.1.19

@author: gaolichuang
'''

import urlparse
import socket
import re


_SUPPORT_CHARSET_ = ['gbk','gb2312','utf-8','big5','latin-1']

def parse_url(url):
    return urlparse.urlparse(url)

def gethost(url):
    return urlparse.urlparse(url).hostname
def gettopdomain(url):
    host = urlparse.urlparse(url).hostname
    return host.split('.')[-1]
def getdomain(url):
    host = urlparse.urlparse(url).hostname
    return '.'.join(host.split('.')[1:])

def gethostname(host):
    try:
        if hasattr(socket, 'setdefaulttimeout'):
            socket.setdefaulttimeout(1)
        return socket.gethostbyname(host)
    except socket.timeout:
        return host

def translate_host(url, ip):
    parse = parse_url(url)
    netloc = parse.netloc
    if "@" in netloc:
        netloc = netloc.rsplit("@", 1)[1]
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]
    target = re.compile(netloc)
    new_netloc = target.sub(ip,parse.netloc)
    another = urlparse.ParseResult(parse.scheme, new_netloc, parse.path, parse.params, parse.query, parse.fragment)
    return urlparse.urlunparse(another)

def normalize_url(url):
    try:
        ip = gethostname(url)
    except:
        ip = gethost(url)
    return translate_host(url,ip)

def get_charset_from_metadata(content, default = 'utf-8'):
    '''get charset from metadata'''
    patten = '<meta[ ]*.*charset[ ]*=[ A-Z-a-z0-9]+\"'
    regx = re.compile(patten)
    ret = regx.findall(content)
    if len(ret) == 0:
        return default
    else:
        substr = ret[0].lower()
    for cset in _SUPPORT_CHARSET_:
        if substr.find(cset) != -1:
            return cset
    return default

if __name__ == '__main__':
    content = '''<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8"></head>
                 <body>
                                                     测试中文页面
                 </body>
                 <meta http-equiv="Content-Typssse" content="text/html;charset=UTF-8">
                 </html>'''
    print get_charset_from_metadata(content)
    content = '''<meta http-equiv="content-type" content="text/html; charset=gb2312" />'''
    print get_charset_from_metadata(content)

    parse_url('http://www.github.com:80/gaolichuang?a=x')
    url = 'http://who:pass@www.github.com:80/gaolichuang?a=x'
    ip = '192.30.252.128'
    new_url = translate_host(url,ip)
    print('before:%s\nafter :%s\nuse ip:%s'%(url,new_url,ip))
    print gethostname('XXX.github.com')
    
