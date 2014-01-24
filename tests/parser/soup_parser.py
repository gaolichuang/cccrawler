# -*- coding: UTF-8 -*- 
'''
Created on 2014.1.23

@author: gaolichuang
http://www.crummy.com/software/BeautifulSoup/
'''
from cccrawler.thirdparty.BeautifulSoup import BeautifulSoup # For processing HTML
from cccrawler.thirdparty.BeautifulSoup import BeautifulStoneSoup # For processing XML

def parse(base_url,content):
    soup = BeautifulSoup(content)
    for a_tag in soup.findAll('a'):
        if not a_tag.has_key('href'):
            continue
        if a_tag.has_key('onclick') or a_tag.has_key('nofollow'):
            continue
        new_url = a_tag['href']
        if base_url and not new_url.startswith("http"):
            new_url = base_url + new_url
        print new_url,a_tag.string

def test():
    soup = BeautifulSoup('<b class="boldest">Extremely bold</b>')
    tag = soup.b
    print tag.name
    print soup.name
    print tag['class']
    print tag.attrs
    print tag.text

def main():
    fp = open('roll.sohu.com.htm','r')
    content = fp.read()
    fp.close()
    soup = BeautifulSoup(content)
    print soup.html.head.title
    print soup.html.head.title.name
    print soup.html.head.title.string
    print soup.title
    parse('http://roll.sohu.com/',content)
    
if __name__ == '__main__':
#    main()
    test()
