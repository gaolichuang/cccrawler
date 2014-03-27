cccrawler
=========
lightweight spider.  

https://docs.google.com/document/d/1X3XrrRTEhDU98dwPZs0XPOdw8-WWMrBrsd0V0YLF40k/edit#

Project address：https://github.com/gaolichuang/cccrawler
定位于100k级别的url抓取，小型的定向抓取需求， 太多后对db的压力会很大，需要升级

### python models

<table>
    <tr>    <td>eventlet</td><td>多任务框架，协程</td></tr>
    <tr>    <td>BeautifulSoup</td><td>抽链</td></tr>
    <tr>    <td>request</td><td>抓取</td></tr>
    <tr>    <td>oslo.config</td><td>配置文件</td></tr>
    <tr>    <td>sqlachemy</td><td>数据库中间件</td></tr>
    <tr>    <td>mmh3</td><td>use for calculate fingerprint https://github.com/hajimes/mmh3</td></tr>
</table>


### FeatureList

<table>
    <tr>    <td>scheduler---dispatch---fetcher---handler</td><td>任务框架</td></tr>
    <tr>    <td>url utils</td><td>对url的normalize，encode 找到schema， host， port， path等</td></tr>
    <tr>    <td>抓取</td><td>目前使用request，支持修改client</td></tr>
    <tr>    <td>content编码检测，编码转换</td><td></td></tr>
    <tr>    <td>抽链</td><td>beautifulsoup</td></tr>
    <tr>    <td>url filter blacklist whitelist 抽链过滤re</td><td></td></tr>
    <tr>    <td>hostload control</td><td>支持泛域名， multifetcher， custom hostload</td></tr>
    <tr>    <td>sqlachldy</td><td>支持sqlite mysql多种db，结果存在db中</td></tr>
    <tr>    <td>去重模块</td><td>memcache</td></tr>
    <tr>    <td>crawldoc checker healthyreport</td><td>待完善</td></tr>
</table>

### TODO

<table>
    <tr>    <td>浏览器抓取</td><td>https://pypi.python.org/pypi/mechanize/<br>http://www.ibm.com/developerworks/cn/linux/l-python-mechanize-beautiful-soup/index.html</td></tr>
    <tr>    <td>支持语言检测</td><td>http://blog.alejandronolla.com/2013/05/15/detecting-text-language-with-python-and-nltk/</td></tr>
    <tr>    <td>抓取</td><td>目前使用request，支持修改client</td></tr>
    <tr>    <td>支持抓pdf，word， img</td><td></td></tr>
    <tr>    <td>crawlmeta， method， referer，custom_accept_type等支持</td><td></td></tr>
    <tr>    <td>抓取进度查询</td><td></td></tr>
    <tr>    <td>wsgi</td><td></td></tr>
    <tr>    <td>支持cookie， 登陆抓取</td><td>memcache</td></tr>
</table>



