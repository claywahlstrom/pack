"""
web module
"""

from subprocess import call as _call
import urllib.request, urllib.error, urllib.parse

from requests import get as _get
from bs4 import BeautifulSoup as _BS

from pack import UNIX as _UNIX, WEB_HDR

LINK = 'http://download.thinkbroadband.com/1MB.zip'

def download(url, title=str(), full_title=False, destination='.', log='DL_log.txt', speed=False):
    """Downloads a url and logs the relevant information"""

    # http://stackoverflow.com/a/16696317/5645103

    assert type(url) == str, 'Lists not supported'

    from datetime import datetime
    import os # for less 'pack' dependencies
    import sys
    from time import time

    import requests

    from pack.web import get_title

    flag = False
    if log:
        logloc = destination+'/'+log
    current = os.getcwd()
    os.chdir(destination) # better file handling
    print('curdir', os.getcwd())

    if not title:
        title, query = get_title(url, full_title)
    else:
        query = None
    f = open(title, 'wb')
    print('Retrieving "{}"...\ntitle {}\nquery {}...'.format(url, title, query))
    try:
        print('size', end=' ')
        if not('.' in title) or 'htm' in title or 'php' in title:
            response = requests.get(url, params=query, headers=WEB_HDR)
            before = time() # start timer
            size = len(response.text)
            print(size, 'bytes')
            f.write(response.text.encode('utf-8'))
            f.close()
        else:
            response = requests.get(url, params=query, headers=WEB_HDR, stream=True)# previously urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDR))
            before = time() # start timer
            size = int(response.headers.get('content-length'))
            CHUNK = size//100
            if CHUNK > 1000000: # place chunk cap on files >1MB
                CHUNK = 100000 # 0.1MB
            print(size, 'bytes')
            print("Writing to file in chunks of {} bytes...".format(CHUNK))
            actual = 0
            try:
                for chunk in response.iter_content(chunk_size=CHUNK):
                    if not chunk: break
                    f.write(chunk)
                    actual += len(chunk)
                    percent = int((actual/size)*100)
                    if 'idlelib' in sys.modules or UNIX:
                        if percent % 5 == 0: # if multiple of 5 reached...
                            print('{}%'.format(percent), end=' ', flush=True)
                    else:
                        os.system('title {}% {}/{}'.format(percent, actual, size))
            except Exception as e:
                print(e)
            finally:
                f.close()
    except Exception as e:
        print('\n'+type(e).__name__, e.args)
        logging = url+' failed\n'
        flag = True
    else:
        taken = time() - before
        print('\ntook {}s'.format(taken))
        if not('idlelib' in sys.modules or UNIX):
            os.system('title Completed {}'.format(title))
        logging = '{} on {} of {} bytes\n'.format(url, datetime.today(), size)
        print('Complete\n')
    finally:
        if not f.closed:
            f.close()
    if log:
        with open(logloc,'a+') as L:
            L.write(logging)
    else:
        print(logging.strip())
    os.chdir(current) # better file handling
    if speed and not(flag):
        return size/taken

def find_href(location, query={}, internal=True, php=False):
    """Extract links. Accepts filename or url"""
    from bs4 import BeautifulSoup as bs
    if not('://' in location):
        with open(location,'r') as bc:
            Read = bc.read()
    else:
        from requests import get
        Read = get(location, headers=WEB_HDR, params=query).content
    soup = bs(Read, 'html.parser')
    raw_links = soup.find_all('a')
    print(raw_links)
    if php or internal:
        links = [x['href'] for x in raw_links if (location[:16] in x['href'] or x['href'].startswith('/')) and not('#' in x['href'])]
        if internal:
            links = [link for link in links if not('?' in link)]
    else:
        links = [link['href'] for link in raw_links]
    return links

def get_file(url):
    """Read response from files"""
    response = urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDR))
    return response.read()

def get_html(page, query=None):
    """Read binary response from webpage"""
    if query is not None:
        assert type(query) == dict
    import requests
    r = requests.get(page, params=query, headers=WEB_HDR)
    text = r.text.encode('utf-8')
    return text

def get_mp3(link, title=str()):
    """Download mp3juice.cc links"""
    from pack.web import download
    if not(title):
        title = link[link.index('=') + 1:] + '.mp3'
    download(link, title=title)

def get_title(url, full=False):
    if '?' in url:
        nurl, query = url.split('?')
    else:
        nurl, query = url, None
    title = nurl.split('/')[-1]
    ext = True
    if [x for x in ['htm', 'aspx', 'php'] if x in title] or ('.' in title and url.count('/') > 2):
        ext = False

    if full:
        title = nurl.replace('://', '_').replace('/', '_')
    if not(title):
        title = 'index'
    if ext:
        title += '.html'
    title = urllib.parse.unquote_plus(title)
    #print('Title', title)
    return title, query

def get_vid(v, vid_type='mp4'):
    """Download using yt-down.tk"""
    from pack.fileops import download
    download('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, v), title='.'.join([v, vid_type]))

def get_web_title(url):
    soup = _BS(_get(url).content, 'html.parser')
    return soup.html.title.text

def openweb(url, browser='firefox'):
    """Open pages in web browsers. "url" can be a list of urls"""

    if type(url) == str:
        url = [url]
    if type(url) == list:
        for link in url:
            if _UNIX:
                _call(['google-chrome', link], shell=True)
            else:
                _call(['start', browser, link.replace('&', '^&')], shell=True)

class WebElements:
    def __init__(self, page=str(), element=str(), method='find_all'):
        if not(page) and not(element):
            page = 'https://www.google.com'
            element = 'a'

        self.source = _get(page)
        self.soup = _BS(self.source.content, 'html.parser')
        self.method = method
        self.element = element
    def find_element(self, element):
        self.__found = eval('self.soup.{}("{}")'.format(self.method, element))
    def get_found(self):
        return self.__found
    def show(self):
        print('Elements:')
        for i in self.get_found(self.element):
            print(i.text)

if __name__ == '__main__':
    print(download(LINK, destination=r'E:\Docs', speed=True), 'bytes per second')
    print(get_title('https://www.minecraft.net/change-language?next=/en/', full=False))
    print(get_title('http://www.google.com/'))
    print(get_title('http://www.google.com'))
    print(get_title(LINK, full=True))
    print('Title:', get_web_title('https://www.google.com'))
    we = WebElements()
    we.find_element()
    we.show()
