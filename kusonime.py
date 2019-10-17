#!/usr/bin/python2
#encoding:UTF-8

import os, sys, argparse, requests
from bs4 import BeautifulSoup as bs
from make_colors import make_colors
from configset import configset
from debug import debug
import clipboard
import re
import pushbullet
import ast
import vping
import sendgrowl
import traceback
from pprint import pprint
from urlparse import urlparse
from aglink import autogeneratelink
import time
import randua
import cmdw
import textwrap
import random
import mimelist
from multiprocessing.pool import ThreadPool
from multiprocessing import Process
#import cfscrape
PID = os.getpid()
IS_SEARCH = False

DOWNLOAD_PATH=None
if os.getenv('DOWNLOAD_PATH'):
    DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH')


class Kusonime(object):
    """docstring for Kusonime"""
    def __init__(self, url='https://kusonime.com'):
        debug()
        super(Kusonime, self).__init__()
        self.url = url
        self.agl = autogeneratelink()
        self.CONFIG = configset()
        self.CONFIGNAME = os.path.join(os.path.dirname(__file__), 'kusonime.ini')
        self.CONFIG.configname = self.CONFIGNAME
        self.proxies = {}
        # print "TIME SLEEP =", self.CONFIG.read_config('SLEEP', 'time', value = '900')
        # print "ALL CONFIG =", self.CONFIG.read_all_config()
        print "\n"
        # self.headers = {}

    def zippyshare_checker(self, url):
        # print "url =", url
        if not re.split("\.", urlparse(url).netloc)[1] == 'zippyshare':
            print make_colors("NOT ZIPPYSHARE URL !", 'lw', 'lr')
            return False
        while 1:
            try:
                a = requests.get(url)
                break
            except:
                pass
        b = bs(a.content, 'lxml')
        c = b.find('div', {'style':'position: relative; float: left; margin: auto; margin-top: 10px; margin-bottom: 10px; padding: 15px 0px 0px 0px; text-align: center; width: 728px; height: 35px; color: #FFFFFF; background-color: #AA0000; font-size: 14px; font-weight: bold;'})
        # print "c =", c
        if c:
            if c.text == u'File does not exist on this server':
                return False
            else:
                return True
        return ""

    def setProxy(self, proxy_ip=None, proxy_port=None):
        debug()
        if proxy_ip and proxy_port:
            self.proxies.update(
                {
                    'http':'http://%s:%s'%(proxy_ip, proxy_port),
                    'https':'https://%s:%s'%(proxy_ip, proxy_port),
                }
            )
        else:
            from proxy_tester import proxy_tester
            pt = proxy_tester.proxy_tester()
            list_proxy_ok = pt.test_proxy_ip(self.url, print_list=True, limit=1)
            debug(list_proxy_ok=list_proxy_ok)
            if list_proxy_ok:
                self.proxies.update({
                    'http': 'http://%s'%(list_proxy_ok[0]),
                    'https': 'https://%s'%(list_proxy_ok[0])
                })

        return self.proxies

    def setHeaders(self, referer='https://neonime.org', accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', accept_encoding = 'gzip, deflate',  accept_language='en-US,en;q=0.5', content_length = '', content_type = '', cookie = '', host = 'neonime.org', origin = '', user_agent = randua.generate(), x_requested_with = ''):
        debug()
        header = {
            'Accept':accept,
            'Accept-Encoding':  accept_encoding,
            'Accept-Language':accept_language,
            'Host': host,
            'Referer':referer,
            'User-Agent':user_agent,
        }
        if not referer:
            referer = 'https://neonime.org'
        if host:
            header.update({'Host': host,})
        if content_length:
            header.update({'Content-Length': content_length,})
        if content_type:
            header.update({'Content-Type': content_type,})
        if cookie:
            header.update({'Cookie': cookie,})
        if origin:
            header.update({'Origin': origin,})
        if x_requested_with:
            header.update({'x-requested-with': x_requested_with,})
        self.headers = header
        debug(self_headers = self.headers)
        debug(header = header)
        return header

    def makeList(self, alist, ncols, vertically=True, file=None):
        debug()
        from distutils.version import StrictVersion # pep 386
        import prettytable as ptt # pip install prettytable
        import sys
        assert StrictVersion(ptt.__version__) >= StrictVersion('0.7') # for PrettyTable.vrules property
        L = alist
        nrows = - ((-len(L)) // ncols)
        ncols = - ((-len(L)) // nrows)
        t = ptt.PrettyTable([str(x) for x in range(ncols)])
        t.header = False
        t.align = 'l'
        t.hrules = ptt.NONE
        t.vrules = ptt.NONE
        r = nrows if vertically else ncols
        chunks = [L[i:i+r] for i in range(0, len(L), r)]
        chunks[-1].extend('' for i in range(r - len(chunks[-1])))
        if vertically:
            chunks = zip(*chunks)
        for c in chunks:
            t.add_row(c)
        print(t)

    def make_icon(self):
        debug()
        f = open(os.path.join(os.path.dirname(__file__), 'img_strings.txt'), 'rb')
        g = open(os.path.join(os.path.dirname(__file__), 'neonime.png'), 'wb')
        g.write(f.read().decode('base64'))
        g.close()
        f.close()
        return os.path.join(os.path.dirname(__file__), g.name)

    def notify(self, text, app='Neonime', event='New Anime', title='Update Anime', host=None, port=None, timeout=20, icon=None, pushbullet_token = None):
        debug()
        debug(host = host)
        if not pushbullet_token:
            pushbullet_token = self.CONFIG.read_config('PUSHBULLET', 'token', value= 'o.gKQr4TEba3t0DSDKLh9IuX4Xaz2oQUSx')
        if pushbullet_token:
            pb = pushbullet.PushBullet(pushbullet_token)
            if vping.vping('8.8.8.8'):
                pb.push_note(app + ' ~ ' + event, text)

        m = sendgrowl.growl()
        if not icon:
            icon = self.make_icon()
        growl_port = self.CONFIG.read_config('GROWL', 'port', value = '23052')
        growl_host = self.CONFIG.read_config('GROWL', 'host', value = '127.0.0.1')
        if growl_host:
            if "," in growl_host:
                host = growl_host.split(",")
            else:
                host = growl_host
        debug(host = host)
        if growl_port:
            #print "growl_port =", growl_port
            port = int(growl_port)
        #if not port:
            #port = 23053
        if isinstance(host, list):
            for i in host:
                debug(i_host = [i])
                try:
                    m.publish(app, event, title, text, str(i).strip(), port, timeout, iconpath=icon)
                except:
                    traceback.format_exc(print_msg = False)
        else:
            debug(host = host)
            try:
                m.publish(app, event, title, text, host, port, timeout, iconpath=icon)
            except:
                traceback.format_exc(print_msg = False)


    def get_update_anime(self, bs_object=None, batch = False, url=None, debugx=False):
        debug()
        if debugx:
            os.environ.update({'DEBUG':'1'})
        debug(batch = batch)
        updates = []
        if not bs_object:
            if not url:
                url = self.url
            a = requests.get(url, proxies=self.proxies)
            bs_object = bs(a.content, 'lxml')
        data = []
        debug(url=url)
        debug(bs_object = bs_object)
        all_items = bs_object.find_all('div', {'class':"item episode-home"})
        debug(all_items=all_items)
        for i in all_items:
            # debug(i=i)
            name = i.find('span', {'class':'tt'}).text
            debug(name=name)
            description = i.find('span', {'class':'ttx'}).text
            description = re.sub('Streaming & Download |Subtitle Indonesia  ', '', description)
            debug(description=description)
            div_fixyear = i.find('div', {'class':'fixyear'})
            episode = div_fixyear.find('h2', {'class':'text-center'}).text
            debug(episode=episode)
            season = i.find('span', {'class':'calidad2 episode'})
            # debug(season=season)
            if season:
                season = season.text
            debug(season=season)
            try:
                url = i.find('div', {'class':'image'}).find('a').get('href')
            except:
                url = i.find('a').get('href')
            debug(url=url)
            thumb = bs(str(i.find('div', {'class':'image'}).find('a')), 'lxml').find('img')#.get('data-src')
            if thumb:
                thumb = thumb.get('data-src')
            else:
                thumb = i.find('div', {'class':'image'}).find('img').get('data-src')
            debug(thumb=thumb)
            updates.append({'name':name, 'description':description, 'url':url, 'episode':episode, 'season':season, 'thumb':thumb})
        debug(updates = updates)
        if not batch:
            pages = self.paginator(bs_object=bs_object)
        else:
            pages = []
        debug(pages = pages)
        return updates, pages

    def get_update_anime_perpage(self, page=1, bs_object=None, url=None, debugx=False):
        debug()
        if debugx:
            os.environ.update({'DEBUG':'1'})
        updates = []
        if not url:
            url = self.url + 'episode/page/' + str(page) + "/"
        debug(url=url)
        if not bs_object:
            while 1:
                try:
                    a = requests.get(url, proxies=self.proxies)
                    break
                except:
                    sys.stdout.write(".")
                    time.sleep(1)
            bs_object = bs(a.content, 'lxml')
        data = []
        # debug(bs_object = bs_object)
        all_items = bs_object.find('table', {'class':"list"}).find('tbody').find_all('tr')
        debug(all_items=all_items)
        for i in all_items:
            # debug(i=i)
            name_pre = i.find('td', {'class':'bb'}).find('a')
            name = name_pre.text.encode('utf-8')
            debug(name=name)
            season_episode = name_pre.find('span')
            episode = ""
            season = ""
            if season_episode:
                season, episode = re.split(":", season_episode.text)
                season = season.encode('utf-8').strip()
                episode = episode.encode('utf-8').strip()
            debug(season=season)
            debug(episode=episode)
            release_pre = i.find('td', {'class':'dd'})
            if release_pre:
                release = release_pre.text
            else:
                release = ""
            url = name_pre.get('href')
            debug(url=url)
            thumb = i.find('div', {'class':'imagen-td'}).find('img')
            if thumb:
                thumb = thumb.get('data-src').encode('utf-8')
            else:
                thumb = thumb.get('src').encode('utf-8')
                if thumb:
                    thumb = thumb.encode('utf-8')
            debug(thumb=thumb)
            updates.append({'name':name, 'url':url, 'episode':episode, 'season':season, 'thumb':thumb})
        debug(updates = updates)
        pages = self.paginator(bs_object=bs_object)
        debug(pages=pages)
        return updates, pages

    def get_new_anime(self, bs_object=None, url=None, debugx=False):
        debug()
        if debugx:
            os.environ.update({'DEBUG':'1'})
        animes = []
        if not bs_object:
            if not url:
                url = self.url
            a = requests.get(url, proxies=self.proxies)
            bs_object = bs(a.content, 'lxml')
        data = []
        all_items = bs_object.find_all('div', {'class':'item'})
        debug(all_items=all_items)
        for i in all_items:
            # debug(i=i)
            name = i.find('span', {'class':'tt'}).text
            name = re.sub(" Subtitle Indonesia", '', name)
            debug(name=name)
            description = i.find('span', {'class':'ttx'}).text
            description = re.sub('Streaming & Download |Subtitle Indonesia  | Subtitle Indonesia', '', description)
            description = re.sub(' : ', ': ', description)
            debug(description=description)
            url = i.find('a').get('href')
            debug(url=url)
            div_fixyear = i.find('div', {'class':'fixyear'})
            year = ''
            year = div_fixyear.find('span', {'class':'year'})
            if year:
                year = year.text

            thumb = i.find('div', {'class':'image'}).find('img')#.get('data-src')
            # debug(thumb=thumb)
            if thumb:
                thumb = thumb.get('data-src')
            else:
                thumb = i.find('div', {'class':'image'}).find('img').get('data-src')
            debug(thumb=thumb)
            animes.append({'name':name, 'description':description, 'url':url, 'year':year, 'thumb':thumb})
        pages = self.paginator(bs_object=bs_object)
        debug(animes=animes)
        return animes, pages

    def get_movies(self, bs_object=None, url=None, debugx=False):
        debug()
        if debugx:
            os.environ.update({'DEBUG':'1'})
        movies = []
        if not url:
            url = self.url
        if not bs_object:
            a = requests.get(url, proxies=self.proxies)
            bs_object = bs(a.content, 'lxml')
        data = []
        all_items = bs_object.find_all('div', {'class':'item'})
        for i in all_items:
            # debug(i=i)
            name = i.find('span', {'class':'tt'}).text
            name = re.sub(" Subtitle Indonesia", '', name)
            debug(name=name)
            description = i.find('span', {'class':'ttx'}).text
            description = re.sub('Streaming & Download |Subtitle Indonesia  | Subtitle Indonesia', '', description)
            description = re.sub(' : ', ': ', description)
            debug(description=description)
            url = i.find('a').get('href')
            debug(url=url)
            div_fixyear = i.find('div', {'class':'fixyear'})
            year = ''
            year = div_fixyear.find('span', {'class':'year'})
            if year:
                year = year.text
            debug(year=year)
            quality = ''
            quality = i.find('span', {'class':'calidad2'})
            if quality:
                quality = quality.text
            debug(quality=quality)
            thumb = i.find('div', {'class':'image'}).find('img')#.get('data-src')
            # debug(thumb=thumb)
            if thumb:
                thumb = thumb.get('data-src')
            else:
                thumb = i.find('div', {'class':'image'}).find('img').get('data-src')
            debug(thumb=thumb)
            movies.append({'name':name, 'description':description, 'url':url, 'year':year, 'quality':quality, 'thumb':thumb})
            debug(movies=movies)
        pages = self.paginator(bs_object=bs_object)
        return movies, pages

    def parse_all_items(self, all_item1):
        debug()
        animes = ''

    def home(self, url = None, set_attrs=True, search = False, batch = False, debugx=False):
        debug()
        debug(url = url, debug=debugx)
        # debug(url = url)
        if not url:
            url = self.url
        if not url:
            print make_colors('NO VALID URL', 'lightwhite', 'lightred')
            sys.exit(0)
        debug(url = url, debug=debugx)
        debug(self_proxies=self.proxies, debug=debugx)
        debug(headers=self.setHeaders(url), debug=debugx)
        while 1:
            try:
                a = requests.get(url, proxies=self.proxies)
                #cf = cfscrape.create_scraper()
                #a = cf.get(url, proxies=self.proxies)
                break
            except:
                sys.stdout.write(".")
                time.sleep(0.5)
        b = bs(a.content, 'lxml')
        #debug(b = b, debug = debugx)
        #pages = self.paginator(bs_object=b, url=url)
        #debug(search = search, debug=debugx)
        #debug(batch = batch, debug=debugx)
        #if search or batch:
            #div_venz = b.find('div', {'id': 'contenedor'}).find('div', {'class': 'contenido',}).find('div', {'class':'box'})
        #else:
        div_venz = b.find('div', {'class':'venz'})
        debug(div_venz = div_venz, debug=debugx)

        RE_CONNECTING = True
        while 1:
            try:
                div_kover = div_venz.find_all('div', {'class':'kover'})
                break
            except:
                if RE_CONNECTING:
                    print "Re:Connecting ."
                    RE_CONNECTING = False
                sys.stdout.write(".")
                time.sleep(1)
        debug(div_kover=div_kover, debug=debugx)
        n = 0
        all_item = {}
        for i in div_kover:
            debug(i = i, debug = debugx)

            thumb = ''
            thumb = i.find('div', {'class': 'thumbz',}).find('img')
            debug(thumb_src = thumb, debug=debugx)
            if thumb:
                thumb = thumb.get('src')
            debug(thumb = thumb, debug=debugx)

            link = i.find('h2', {'class': 'episodeye',}).find('a')
            debug(link_src = link, debug=debugx)

            name = link.get('title')
            debug(name = name, debug=debugx)

            link = link.get('href')
            debug(link = link, debug=debugx)
            all_p = i.find_all('p')
            debug(all_p = all_p, debug=debugx)

            posted = all_p[0].text.strip()

            debug(posted = posted, debug=debugx)
            release = all_p[1].text.strip()

            debug(release = release, debug=debugx)
            genres = {}
            all_genres = all_p[2].find_all('a')
            debug(all_genres = all_genres, debug=debugx)
            for g in all_genres:
                genres.update(
                    {
                        g.text: g.get('href')
                    }
                )
            debug(genres = genres, debug=debugx)
            
            all_item.update({
                n: {
                    'name': name,
                    'link': link,
                    'thumb': thumb,
                    'posted': posted,
                    'release': release,
                    'genres': genres,

                }
            })
            n += 1
        print "-" * cmdw.getWidth()
        debug(all_item = all_item, debug = True)
        #pprint(all_item)
        #if batch:
            #all_item1 = div_box_item.find_all('div', {'class':'items'})
        #else:
            #all_item1 = div_box_item.find_all('div', {'class':'item_1 items'})
        #debug(all_item1=all_item1, debug=debugx)
        #statistic_anime = self.statistic('anime', b)
        #statistic_movie = self.statistic('movie', b)
        #debug(all_item1=all_item1)

        #if set_attrs:
            #if search:
                #search_anime = self.get_update_anime(all_item1[0])
                #setattr(self, "search_anime", search_anime)
                #return search_anime
            #elif batch:
                #batch_anime = self.get_update_anime(all_item1[0], True)
                #setattr(self, "batch_anime", batch_anime)
                #return batch_anime
            #else:
                #update_anime = self.get_update_anime(all_item1[0])
                #new_anime = self.get_new_anime(all_item1[1])
                #new_movies = self.get_movies(all_item1[2])
                #debug(update_anime = update_anime, debug=debugx)
                #debug(new_anime = new_anime, debug=debugx)
                #debug(new_movies = new_movies, debug=debugx)

                #setattr(self, "update_anime", update_anime)

                #setattr(self, "new_anime", new_anime)

                #setattr(self, "new_movies", new_movies)

                #return update_anime, new_anime, new_movies, statistic_anime, statistic_movie, pages
        #else:
            #debug(all_item1=all_item1)
            #return (all_item1)

    def paginator(self, class_name='dd', bs_object=None, page_type=None, url=None):
        debug()
        #page_type: anime, movies, release
        pages = {}

        if page_type:
            all_item1 = self.home(False)
            if page_type == 'anime':
                bs_object = all_item1[0]
            elif page_type == 'movies':
                bs_object = all_item1[2]
            elif page_type == 'release':
                bs_object = all_item1[1]
        if not bs_object:
            if not url:
                url = self.url
            a = requests.get(url, proxies=self.proxies)
            bs_object = bs(a.content, 'lxml')
        div_paginado = bs_object.find_all('div', {'class': 'paginado'})
        debug(div_paginado=div_paginado)
        # sys.exit(0)
        n = 1
        for p in div_paginado:
            pages_per_page = []
            all_li = p.find('ul').find_all('li')
            for i in all_li:
                if not i.text:
                    all_li.remove(i)
                elif i.text.strip() == "...":
                    all_li.remove(i)
            debug(all_li=all_li)
            current_page = p.find('ul').find('li', {'class':class_name}).find('a').text
            pages_per_page.append({'current_page':current_page})
            next_page = all_li[1].find('a').get('href')
            pages_per_page.append({'next_page':next_page})
            last_page = all_li[-1].find('a').get('href')
            pages_per_page.append({'last_page':last_page})
            for i in all_li[1:]:
                page = i.find('a').get('href')
                page_name = i.find('a').text
                pages_per_page.append({page_name:page})
            debug(pages=pages)
            pages.update({n:pages_per_page})
            n+=1
        return pages

    def get_anime_details(self, url='https://neonime.org/episode/persona-5-the-animation-1x25/'):
        debug()
        debug(url=url)
        debug(self_proxies=self.proxies)
        all_episode = []
        all_download = []
        infos = {}
        if not url:
            print make_colors('NO URL DETAIL', 'lightwhite', 'lightred', attrs=['blink'])
            return False
        while 1:
            try:
                a = requests.get(url, proxies=self.proxies)
                break
            except:
                pass
        b = bs(a.content, 'lxml')
        div_contenedor = b.find('div', {'id':'contenedor'}).find('div', {'class':'tvshows_single contenido'})
        general_info = div_contenedor.find('div', {'id':'series'})
        poster = general_info.find('div', {'class':'ladoA'}).find('div', {'id':'fixar'}).find('div', {'class':'imagen'}).find('img').get('data-src')
        infos.update({'poster':poster})
        # print "poster =", poster
        debug(poster=poster)
        url = general_info.find('div', {'class':'ladoA'}).find('div', {'class':'imagen'}).find('a').get('href')
        debug(url=url)
        infos.update({'url':url})
        date = general_info.find('div', {'class':'ladoA'}).find('div', {'class':'meta-a'}).find('p').text
        infos.update({'date':date})
        season_episode = general_info.find('div', {'class':'ladoA'}).find('div', {'class':'meta-b'}).find_all('span')
        debug(season_episode=season_episode)
        season = season_episode[0].find('i').text#.find('span', {'class':'metx'}).text
        infos.update({'season':season})
        debug(season=season)
        episode = season_episode[1].find('i').text#.find('span', {'class':'metx'}).text
        infos.update({'episode':episode})
        debug(episode=episode)
        epinav = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'metax1'}).find('div', {'class':'epinav'})
        debug(epinav=epinav)
        epinav_select = epinav.find('select')
        if epinav_select:
            all_episode_links = epinav_select.find_all('option')
            debug(all_episode_links=all_episode_links)
            for i in all_episode_links:
                all_episode.append({'name':i.text.strip(), 'url':i.get('value')})
        else:
            all_episode.append({'name': "Episode " + str(episode), 'url':url})
            debug(all_episode=all_episode)
            next_episode = epinav.find('a', {'class':'navtv'})
            debug(next_episode=next_episode)
            all_episode.append({'name': "Episode " + str(int(episode) + 1), 'url': next_episode.get('href')})
            debug(all_episode=all_episode)

        debug(all_episode=all_episode)
        #all_download_links_li = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'enlaces_box'}).find_all('ul', {'class':'enlaces'})[1].find_all('li') #old fashion
        all_download_links_ul = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'linkstv'}).find('div', {'class': 'sbox'}).find_all('ul')
        debug(all_download_links_ul=all_download_links_ul)
        debug(all_download_links_li_0=all_download_links_ul[0])
        #sys.exit(0)
        thumb = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'cover'}).get('style')
        thumb = re.findall('https.*?.jpg', thumb)[0]
        infos.update({'thumb':thumb})
        debug(thumb=thumb)
        backdrops = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'backdropss'}).find('div', {'class': 'galeria_img'}).find('img').get('data-src')
        debug(backdrops=backdrops)
        infos.update({'backdrops':backdrops})
        sinopsis_pre = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'contenidotv'}).find('div', {'itemprop': 'description'}).find_all('p')
        debug(sinopsis_pre=sinopsis_pre)
        sinopsis = ""
        if sinopsis_pre:
            if len(sinopsis_pre) > 1:
                for i in sinopsis_pre[1:]:
                    sinopsis += " " + i.text
            else:
                sinopsis = sinopsis_pre[0].text
            sinopsis = re.sub("neonime", "akanime", sinopsis, re.I)
            debug(sinopsis=sinopsis)
        infos.update({'sinopsis':sinopsis})
        all_metadatac = general_info.find('div', {'class':'ladoB'}).find('div', {'id':'info'}).find_all('div', {'class':'metadatac'})
        for i in all_metadatac:
            if i.find('b').text == 'Air date':
                air_date = i.find('span').text
                debug(air_date=air_date)
                infos.update({'air_date':air_date})
            elif i.find('b').text == 'Serie':
                name = re.sub("Subtitle|Indonesia", "", i.find('span').find('a').text).strip()
                debug(name=name)
                infos.update({'name':name})
            elif i.find('b').text == 'Source':
                source = i.find('span').text
                debug(source=source)
                infos.update({'source':source})
            elif i.find('b').text == 'Genre':
                genres = {}
                for j in i.find('span').find_all('a'):
                    genres.update({
                        j.text: j.get('href')
                    })
                debug(genres=genres)
                infos.update({'genres':genres})
        debug(infos=infos)
        all_downloads = []
        for i in all_download_links_ul[0].find_all('ul'):
            debug(i = i)

            data_li = i.find('li')
            debug(data_li = data_li)
            quality = data_li.find('label', {'class': 'label-download',}).text
            if 'HD' in quality:
                quality += " (MP4)"
            elif "MKV" in quality:
                quality += " (MKV)"
            else:
                quality += " (MP4)"
            links = data_li.find_all('a')
            debug(links = links)
            for a in links:
                data_link = {}
                data_link.update({
                    'name': a.text,
                    'link': a.get('href'),
                   'quality': quality,
                })
                debug(data_link = data_link)
                all_downloads.append(data_link)
                debug(all_downloads = all_downloads)
            #print "=" * 120

            #link = i.find('a').get('href')
            #debug(link=link)
            #name = i.find('a').find('span', {'class':'b'}).text.strip()
            #debug(name=name)
            #lang = i.find('a').find('span', {'class':'c'}).text
            #debug(lang=lang)
            #quality = i.find('a').find('span', {'class':'d'}).text
            #debug(quality=quality)
            #all_download.append({
                #'name':name,
                            #'link':link,
                                #'lang':lang,
                                #'quality':quality
            #})
        debug(all_downloads=all_downloads)
        return all_downloads, all_episode, infos

    def get_new_anime_details(self, url='https://neonime.org/tvshows/hero-mask-subtitle-indonesia/'):
        debug()
        all_episode = []
        all_download = []
        infos = {}
        if not url:
            print make_colors('NO URL DETAIL', 'lightwhite', 'lightred', attrs=['blink'])
            return False
        a = requests.get(url, proxies=self.proxies)
        b = bs(a.content, 'lxml')
        div_contenedor = b.find('div', {'id':'contenedor'}).find('div', {'class':'tvshows_single contenido'})
        general_info = div_contenedor.find('div', {'id':'series'})
        poster = general_info.find('div', {'class':'ladoA'}).find('div', {'id':'fixar'}).find('div', {'class':'imagen'}).find('img').get('data-src')
        infos.update({'poster':poster})
        debug(poster=poster)
        jpname = general_info.find('div', {'class':'ladoA'}).find('div', {'class':'meta-a'}).find('p').text
        infos.update({'jpname':jpname})
        season_episode = general_info.find('div', {'class':'ladoA'}).find('div', {'class':'meta-b'}).find_all('span')
        debug(season_episode=season_episode)
        season = season_episode[0].find('i').text#.find('span', {'class':'metx'}).text
        infos.update({'season':season})
        debug(season=season)
        episode = season_episode[1].find('i').text#.find('span', {'class':'metx'}).text
        infos.update({'episode':episode})
        debug(episode=episode)

        all_episode_links = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'id':'seasons'}).find('div', {'class':'se-a'}).find('ul', {'class':'episodios'}).find_all('li')
        debug(all_episode_links=all_episode_links)

        for i in all_episode_links:
            number = i.find('div', {'class':'numerando'}).text
            debug(number=number)
            link = i.find('div', {'class':'episodiotitle'}).find('a').get('href')
            debug(link=link)
            name = i.find('div', {'class':'episodiotitle'}).find('a').text
            debug(name=name)
            date = i.find('span', {'class':'date'}).text
            debug(date=date)
            all_episode.append(
                {
                    'name':name,
                    'number': number ,
                    'url':link,
                    'date':date
                }
            )
        debug(all_episode=all_episode)
        name = re.sub("Subtitle|Indonesia", "", general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('h1', {'itemprop':'name'}).text, re.I).strip()
        infos.update({'name':name})

        # genres_links = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'metadatac'}).find('span').find_all('a')
        # debug(genres_links=genres_links)

        backdrops = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'backdropss'}).find('div', {'class': 'galeria_img'}).find('img').get('data-src')
        debug(backdrops=backdrops)
        infos.update({'backdrops':backdrops})
        sinopsis_pre = general_info.find('div', {'class':'ladoB'}).find('div', {'class':'central'}).find('div', {'class':'contenidotv'}).find('div', {'itemprop': 'description'}).find_all('p')
        sinopsis = ""
        for i in sinopsis_pre:
            sinopsis += " " + i.text
        sinopsis = re.sub("neonime", "akanime", sinopsis, re.I)
        debug(sinopsis=sinopsis)
        infos.update({'sinopsis':sinopsis})
        all_metadatac = general_info.find('div', {'class':'ladoB'}).find('div', {'id':'info'}).find_all('div', {'class':'metadatac'})
        release = {}
        for i in all_metadatac:
            if i.find('b').text == 'Release Year':
                release_url = i.find('span').find('a').get('href')
                release_year = i.find('span').find('a').text
                release.update({'year':release_year, 'url':release_url})
                debug(release=release)
                infos.update({'release':release})
            elif i.find('b').text == 'Firt air date':
                first_air_date = i.find('span').text
                debug(first_air_date=first_air_date)
                infos.update({'first_air_date':first_air_date})
            elif i.find('b').text == 'Last air date':
                last_air_date = i.find('span').text
                debug(last_air_date=last_air_date)
                infos.update({'last_air_date':last_air_date})
            elif i.find('b').text == 'Type':
                anime_type = i.find('span').text
                debug(anime_type=anime_type)
                infos.update({'anime_type':anime_type})
            elif i.find('b').text == 'Episode runtime':
                episode_runtime = i.find('span').text
                debug(episode_runtime=episode_runtime)
                infos.update({'episode_runtime':episode_runtime})
            elif i.find('b').text == 'TV Status':
                tv_status = i.find('span').text
                debug(tv_status=tv_status)
                infos.update({'tv_status':tv_status})
            elif i.find('b').text == 'Genre':
                genres = {}
                for j in i.find('span').find_all('a'):
                    genres.update({
                        j.text: j.get('href')
                    })
                debug(genres=genres)
                infos.update({'genres':genres})
        debug(all_episode=all_episode)
        debug(infos=infos)
        return all_episode, infos

    def get_movie_details(self, url='https://neonime.org/koi-wa-ameagari-no-you-ni-live-action-subtitle-indonesia/'):
        debug()

        all_download = []
        infos = {}
        if not url:
            print make_colors('NO URL DETAIL', 'lightwhite', 'lightred', attrs=['blink'])
            return False
        a = requests.get(url, proxies=self.proxies)
        b = bs(a.content, 'lxml')
        div_contenedor = b.find('div', {'id':'contenedor'}).find('div', {'id':'single'})
        poster = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'sbox'}).find('div', {'class':'imagen'}).find('img').get('data-src')
        debug(poster=poster)
        infos.update({'poster':poster})
        name = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'data'}).find('h1').text
        name = re.sub("Subtitle|Indonesia", "", name, re.I).strip()
        debug(name=name)
        infos.update(name=name)
        jpname = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'data'}).find('span', {'class':'titulo_o'}).find('i', {'itemprop':'name'}).text
        debug(jpname=jpname)
        date = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'data'}).find('span', {'class':'titulo_o'}).find('i', {'itemprop':'datePublished'}).text
        debug(date=date)
        infos.update({'jpname':jpname})
        infos.update({'date':date})
        imdb_enc = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'data'}).find('div', {'class':'imdb_r'}).find('div', {'class':'b'}).find('span', {'class':'dato'}).find('a').get('href')
        debug(imdb_enc=imdb_enc)
        if urlparse(imdb_enc).netloc == 'hightech.web.id':
            imdb = re.split('site=', urlparse(imdb_enc).query)[1].decode('base64')
        else:
            imdb = imdb_enc
        debug(imdb=imdb)
        infos.update({'imdb':imdb})
        all_description = div_contenedor.find('div', {'class':'s_left'}).find('div', {'class':'entry-content'}).find('div', {'id':'cap1'}).find_all('p')[1:3]
        debug(all_description=all_description)
        description = []
        for i in all_description:
            description.append(i.text)
        description = " ".join(description)
        description = re.sub("neonime", "akanime", description, re.I)
        debug(description=description)
        infos.update({'description':description})
        screenshot = div_contenedor.find('div', {'class':'s_left'}).find('div', {'id':'backdrops'}).find('div', {'class':'galeria_img'}).find('img').get('data-src')
        debug(screenshot=screenshot)
        infos.update({'screenshot':screenshot})
        all_download_links_ul = div_contenedor.find('div', {'class':'s_left'}).find_all('div', {'class': 'sbox'})[2].find_all('ul')
        debug(all_download_links_ul=all_download_links_ul)
        debug(infos=infos)
        for i in all_download_links_ul[0].find_all('ul'):
            debug(i = i)

            data_li = i.find('li')
            debug(data_li = data_li)
            quality = data_li.find('label', {'class': 'label-download',}).text
            if 'HD' in quality:
                quality += " (MP4)"
            elif "MKV" in quality:
                quality += " (MKV)"
            else:
                quality += " (MP4)"
            links = data_li.find_all('a')
            debug(links = links)
            for a in links:
                data_link = {}
                data_link.update({
                    'name': a.text,
                    'link': a.get('href'),
                   'quality': quality,
                })
                debug(data_link = data_link)
                all_download.append(data_link)
                debug(all_download = all_download)
        debug(all_download=all_download)
        return all_download, infos

    def search(self, query = "Boruto", search_url=None):
        debug()
        if not self.url:
            print make_colors('NO VALID URL', 'lightwhite', 'lightred')
            sys.exit(0)
        if not search_url:
            search_url = "{0}?s={1}".format(self.url, query)
        return self.home(search_url, search= True)

    def get_batch_anime(self, url=None):
        debug()
        if not url:
            if not self.url:
                print make_colors('NO VALID URL', 'lightwhite', 'lightred')
                sys.exit(0)
            else:
                url = self.url
        batch_url = url + 'batch/'
        all_batch = []
        all_item = self.home(batch_url, False, batch= True)[0]
        debug(all_item = all_item)
        all_div_item = all_item.find_all('div', {'class': 'item',})
        debug(all_div_item = all_div_item)
        for i in all_div_item:
            url = i.find('a').get('href')
            debug(url = url)
            thumb = i.find('div', {'class': 'img'}).find('img').get('src')
            debug(thumb = thumb)
            name = i.find('a').find('span', {'class': 'title',}).text
            debug(name = name)
            airtime = i.find('div', {'class': 'dato',}).text
            debug(airtime = airtime)
            all_batch.append({'name': name, 'url': url, 'thumb': thumb, 'airtime': airtime,})
        debug(all_batch = all_batch)
        return all_batch

    def get_batch_detail_item(self, div_single, strings):
        debug()
        debug(div_single = div_single, debug = True)
        if isinstance(strings, list):
            strings = "|".join(strings)
        item = div_single.find('span', text = re.compile(strings, re.I))
        item_parent = ''
        if item:
            item_parent = item.parent.text.encode('utf-8')
        if item_parent:
            return re.sub(strings, '', item_parent, flags = re.I).strip()
        return ''

    def get_batch_detail(self, url_batch):
        debug()
        a = requests.get(url_batch, proxies=self.proxies)
        b = bs(a.content, 'lxml')
        div_single = b.find('div', {'id': 'contenedor',}).find('div', {'id': 'single',}).find('div', {'class': 'entry-content',})
        debug(div_single = div_single)
        all_p = div_single.find_all('p')
        debug(all_p = all_p)

        batchs = {}

        name = div_single.find('h1').text
        episode = self.get_batch_detail_item(div_single, "episodes:")
        aired = self.get_batch_detail_item(div_single, "aired:")
        premiered = self.get_batch_detail_item(div_single, "premiered:")
        broadcast = self.get_batch_detail_item(div_single, "broadcast:")
        producers = self.get_batch_detail_item(div_single, ["producers:", "add some"])
        licensors = self.get_batch_detail_item(div_single, "licensors:|add some")
        studios = self.get_batch_detail_item(div_single, "studios:")
        source = self.get_batch_detail_item(div_single, "source:")
        genres = self.get_batch_detail_item(div_single, "genres:")
        duration = self.get_batch_detail_item(div_single, "duration:")
        rating = self.get_batch_detail_item(div_single, "rating:")
        score = self.get_batch_detail_item(div_single, "score:")
        score = self.get_batch_detail_item(div_single, "score:")
        by = div_single.find('p', text = re.compile('by ', re.I))
        if by:
            by = by.text.strip()
        download_links = []
        n = 1
        all_download_links = div_single.find_all('p', {'class': 'name',})
        if all_download_links:
            for i in all_download_links:
                links = []
                batch_name = i.find('strong')
                if batch_name:
                    batch_name = batch_name.text.encode('utf-8')
                all_download_links_a = i.find_all('a')
                for x in all_download_links_a:
                    links.append({'url': x.get('href'), 'name': x.text,})
                download_links.append({batch_name: links})


        if os.getenv('DEBUG_SERVER') or os.getenv('DEBUG'):
            import random
            from make_colors_tc import make_colors as make_colors_tc
            random_color = ['lightwhite', 'lightblue', 'lightyellow', 'lightmagenta', 'lightgreen', 'lightred']
            print "name      =", make_colors_tc(name, random.choice(random_color))
            print "episode   =", make_colors_tc(episode, random.choice(random_color))
            print "aired     =", make_colors_tc(aired, random.choice(random_color))
            print "premiered =", make_colors_tc(premiered, random.choice(random_color))
            print "broadcast =", make_colors_tc(broadcast, random.choice(random_color))
            print "producers =", make_colors_tc(producers, random.choice(random_color))
            print "licensors =", make_colors_tc(licensors, random.choice(random_color))
            print "studios   =", make_colors_tc(studios, random.choice(random_color))
            print "source    =", make_colors_tc(source, random.choice(random_color))
            print "genres    =", make_colors_tc(genres, random.choice(random_color))
            print "duration  =", make_colors_tc(duration, random.choice(random_color))
            print "rating    =", make_colors_tc(rating, random.choice(random_color))
            print "score     =", make_colors_tc(score, random.choice(random_color))
            print "by        =", make_colors_tc(by, random.choice(random_color))
            import pprint
            print "download_links ="
            pprint.pprint(download_links)

        description = all_p[2]
        if description:
            description = all_p[2].text.encode('utf-8')
        print "description =", description
        batchs.update({
            'name': name,
            'episode': episode,
            'aired': aired,
                    'premiered': premiered,
                    'broadcast': broadcast,
                    'producers': producers,
                    'licensors': licensors,
                    'studios': studios,
                    'source': source,
                    'genres': genres,
                    'duration': duration,
                    'rating': rating,
                    'score': score,
                    'by': by,
                    'description': description,
                    'download_links': download_links,
        })

        debug(batchs = batchs)
        return batchs

    def menu(self, menu = None):
        debug()
        """
        	menu: - home (default)
        		  - movies
        		  - anime
        		  - batch
        		  - semua
        		  - tvshows
        """
        menu_items = {
            'home': self.url,
            'movies': self.url + 'movies/',
            'anime': self.url,
                    'batch': self.url + 'batch',
                    'semua': self.url + 'semua/',
                    'tvshows': self.url + 'tvshows/',
        }
        if menu:
            try:
                if str(menu).lower() in menu_items.keys():
                    return menu_items.get(str(menu).lower())
                else:
                    return self.url
            except:
                return self.url
        else:
            return self.url

    def statistic(self, id = 'anime', bs_objects = None):
        debug()
        debug(id=id)
        if not bs_objects:
            a = requests.get(self.url, proxies=self.proxies)
            bs_objects = bs(a.content, 'lxml')
        # if id == 'anime':
        #     b = bs_objects.find('div', {'id': 'serieshome',})
        # elif id == 'movie':
        #     b = bs_objects.find('div', {'id': 'moviehome',})
        # else:
        #     return []
        category = bs_objects.find('div', {'class': 'categorias'}).find('h3').text.strip()
        debug(category = category)
        items = []
        items_lis = bs_objects.find_all('li', {'class': re.compile('cat-item'),})
        debug(items_lis = items_lis)
        for i in items_lis:
            items.append(
                {
                    'name': i.find('a').text,
                    'url': i.find('a').get('href'),
                                'score': i.find('span').text,
                })
        debug(items = items)
        return items

    def check_data_monitor(self, data1 ,data2):
        debug()
        if data:
            pass

    def monitor(self, use_proxy=False):
        print make_colors('Monitoring start ...', 'black', 'lightyellow')
        self.home()
        data_anime = ''
        data_new_anime = ''
        data_movies = ''

        data_anime = self.update_anime[0]
        data_new_anime = self.new_anime[0]
        data_movies = self.new_movies[0]

        data_keys_anime = []
        data_keys_new_anime = []
        data_keys_movies = []

        while 1:
            for i in data_anime:
                data_keys_anime.append(i.get('name'))
            for i in data_new_anime:
                data_keys_new_anime.append(i.get('name'))
            for i in data_movies:
                data_keys_movies.append(i.get('name'))
            debug(data_keys_anime = data_keys_anime)
            debug(data_keys_new_anime = data_keys_new_anime)
            debug(data_keys_movies = data_keys_movies)

            _data_keys_anime = []
            _data_keys_new_anime = []
            _data_keys_movies = []

            self.home()
            _data_anime = self.update_anime[0]
            _data_new_anime = self.new_anime[0]
            _data_movies = self.new_movies[0]

            for i in _data_anime:
                _data_keys_anime.append(i.get('name'))
            for i in _data_new_anime:
                _data_keys_new_anime.append(i.get('name'))
            for i in _data_movies:
                _data_keys_movies.append(i.get('name'))
            debug(_data_keys_anime = _data_keys_anime)
            debug(_data_keys_new_anime = _data_keys_new_anime)
            debug(_data_keys_movies = _data_keys_movies)

            print make_colors('Monitoring ANIME', 'black', 'lightgreen')
            for i in _data_keys_anime:
                if not i in data_keys_anime:
                    img = self.downloadImage([_data_keys_anime[_data_keys_anime.index(i)].get('thumb')], use_proxy)
                    self.notify(_data_keys_anime[_data_keys_anime.index(i)].get('name'), icon= img)

            print make_colors('Monitoring NEW ANIME', 'lightwhite', 'lightmagenta')
            for i in _data_keys_new_anime:
                if not i in data_keys_new_anime:
                    img = self.downloadImage([_data_keys_new_anime[_data_keys_new_anime.index(i)].get('thumb')], use_proxy)
                    self.notify(_data_keys_new_anime[_data_keys_new_anime.index(i)].get('name'), icon= img)

            print make_colors('Monitoring MOVIES', 'lightwhite', 'lightblue')
            for i in _data_keys_movies:
                if not i in data_keys_movies:
                    img = self.downloadImage([_data_keys_movies[_data_keys_movies.index(i)].get('thumb')], use_proxy)
                    self.notify(_data_keys_movies[_data_keys_movies.index(i)].get('name'), icon= img)

            data_anime = _data_anime
            data_new_anime = _data_new_anime
            data_movies = _data_movies
            time.sleep(int(self.CONFIG.read_config('SLEEP', 'time', value = '900')))

    def monitor1(self, use_proxy=False):
        print make_colors('Monitoring start ...', 'black', 'lightyellow')
        self.home()
        debug()
        update_anime = self.update_anime[0]
        new_anime = self.new_anime[0]
        new_movies = self.new_movies[0]
        def check(data, dtype='anime'):

            while 1:
                self.home()
                if dtype == 'anime':
                    data_1 = self.update_anime[0]
                elif dtype == 'new_anime':
                    data_1 = self.new_anime[0]
                elif dtype == 'movies':
                    data_1 = self.new_movies[0]
                else:
                    print make_colors('No DTYPE Input !' ,'lightwhite', 'lightred')
                    return False

                data_2 = data_1
                for i in data:
                    debug(i = i)
                    for x in data_1:
                        try:
                            if i.get('name') == x.get('name'):
                                data_1.remove(x)
                        except:
                            pass
                        try:
                            if i.get('name') == x.get('name'):
                                del(data_1[data_1.index(x)])
                        except:
                            pass
                print "data_1 =", data_1
                print "time sleep =", time.sleep(int(self.CONFIG.read_config('SLEEP', 'time', value = '900')))
                print "-"*220
                if len(data_1) > 0:
                    # def notify(self, text, app='Neonime', event='New Anime', title='Update Anime', host=None, port=None, timeout=20, icon=None, pushbullet_token = None)
                    for i in data_1:
                        # def downloadImage(self, list_images, use_proxy=False)
                        img = self.downloadImage([data_1[data_1.index(i)].get('thumb')], use_proxy)
                        if not img:
                            img = None
                        else:
                            img = img[0]
                        self.notify(data_1[data_1.index(i)].get('name'), icon= img)
                    data = data_2
                    time.sleep(int(self.CONFIG.read_config('SLEEP', 'time', value = '900')))
                    # self.home()
                else:
                    data = data_2
                    time.sleep(int(self.CONFIG.read_config('SLEEP', 'time', value = '900')))
                    # self.home()
        pool = ThreadPool(processes= 3)
        # tx = pool.apply_async(tkimage.showImages, args)
        # tx1 = Process(target=check, args=(update_anime, 'anime'))
        # tx2 = Process(target=check, args=(new_anime, 'new_anime'))
        # tx3 = Process(target=check, args=(new_movies, 'movies'))
        print make_colors('Monitoring ANIME', 'black', 'lightgreen')
        tx1 = pool.apply_async(check, (update_anime, 'anime'))
        print make_colors('Monitoring NEW ANIME', 'lightwhite', 'lightmagenta')
        tx2 = pool.apply_async(check, (new_anime, 'new_anime'))
        print make_colors('Monitoring MOVIES', 'lightwhite', 'lightblue')
        tx3 = pool.apply_async(check, (new_movies, 'movies'))


        # tx1.start()

        # tx2.start()

        # tx3.start()
        while 1:
            try:
                time.sleep(int(self.CONFIG.read_config('SLEEP', 'time', value = '900')))
            except KeyboardInterrupt:
                break
        print make_colors('Monitor STOPPED !', 'lightwhite', 'lightred')
        sys.exit(0)

    def download(self, url=None, dtype=None, pcloud=False, agl=True, download_path = os.getcwd(), provider=None, provider_quality=None, all_download=None, name=None, use_proxy=False):
        '''
            dtype: anime, new_anime, movie
        '''
        debug()
        debug(dtype=dtype)
        debug(url=url)

        if not all_download:
            if not url:
                print make_colors('No URL given !', 'lightwhite', 'lightred')
                return False
            if dtype == 'anime':
                all_download, all_episode, infos = self.get_anime_details(url)
                debug(all_episode=all_episode)
            elif dtype == 'movie':
                # print "movie ..."
                all_download, infos = self.get_movie_details(url)
            debug(infos=infos)
            if not name:
                name = infos.get('name').encode('utf-8')
        if name:
            print make_colors("NAME: ", 'black', 'lightcyan') + make_colors(infos.get('name').encode('utf-8'), 'b', 'lg')
        debug(all_download=all_download)
        download_provider_url = None
        if provider and provider_quality:
            for i in all_download:
                if i.get('name').lower() == provider.lower() and i.get('quality').lower() == provider_quality.lower():
                    download_provider_url = i.get('link')
                    break
                else:
                    pass

        if not download_provider_url:
            for i in all_download:
                number = all_download.index(i)
                if len(str(number)) == 1 and not number == 9:
                    number = "0" + str(number + 1)
                else:
                    number = str(number + 1)
                #if re.split("\.", urlparse(i.get('link')).netloc)[1] == 'zippyshare':
                    # #check = self.zippyshare_checker(i.get('link'))
                    #check = True
                    # # print "check =", check
                    #if isinstance(check, bool):
                        #if not check:
                            #print " " * 4 + number + ". " + make_colors(i.get('name'), 'lightgreen') + " [" + make_colors(i.get('quality').encode('utf-8'), 'lightwhite', 'lightmagenta') + "] (" + make_colors(i.get('lang'), 'lightwhite' , 'lightblue') + ")" + " [" + make_colors("ERROR", 'lightwhite', 'lightred', ['blink']) + "]"
                        #else:
                            #print " " * 4 + number + ". " + make_colors(i.get('name'), 'lightgreen') + " [" + make_colors(i.get('quality').encode('utf-8'), 'lightwhite', 'lightmagenta') + "] (" + make_colors(i.get('lang'), 'lightwhite' , 'lightblue') + ")"
                    #else:
                        #print " " * 4 + number + ". " + make_colors(i.get('name'), 'lightgreen') + " [" + make_colors(i.get('quality'), 'lightwhite', 'lightmagenta') + "] (" + make_colors(i.get('lang'), 'lightwhite' , 'lightblue') + ")" + " " + make_colors(check, 'lightwhite', 'lightred', ['blink'])
                #else:
                print " " * 4 + number + ". " + make_colors(i.get('name'), 'lightgreen').encode('utf-8') + " [" + make_colors(i.get('quality').encode('utf-8'), 'lightwhite', 'lightmagenta') + "]"  # "] (" + make_colors(i.get('lang'), 'lightwhite' , 'lightblue') + ")"
            qs = raw_input(make_colors("Select Number to download or option: ", 'black', 'lightyellow'))
            # print "DOWNLOAD_PATH =", download_path
            debug(all_download=all_download)
            if str(qs).isdigit():
                if not int(qs) > len(all_download):
                    debug(url = all_download[int(qs)-1].get('link'))
                    print make_colors("URL", 'lw','lm') + ": " + make_colors(all_download[int(qs)-1].get('link'), 'lg')
                    downloading = self.agl.generate(all_download[int(qs)-1].get('link'), True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
                    debug(downloading=downloading)
                    if downloading == "Link Dead! or Host is temporarily down! Generate again after 5 minutes!" or not downloading or downloading == 'Generate Failed!':
                        qs1 = raw_input(make_colors("re-Download Again (y[es]/n[o]/a[uto]): ", 'lightwhite', 'lightred'))
                        if qs1.lower() == 'y' or qs1.lower() == 'yes':
                            return self.download(url, dtype, pcloud, agl, download_path, provider, provider_quality, all_download)
                        elif qs1.lower() == 'a' or qs1.lower() == 'auto':
                            while 1:
                                if downloading == "Link Dead! or Host is temporarily down! Generate again after 5 minutes!" or not downloading or downloading == 'Generate Failed!':
                                    downloading = self.agl.generate(all_download[int(qs)-1].get('link'), True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
                                    debug(downloading=downloading)
                                else:
                                    break

        else:
            debug(download_provider_url=download_provider_url)
            downloading = self.agl.generate(download_provider_url, True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
            debug(downloading=downloading)
            if downloading == "Link Dead! or Host is temporarily down! Generate again after 5 minutes!" or not downloading:
                qs1 = raw_input(make_colors("re-Download Again (y[es]/n[o]/a[uto]): ", 'lightwhite', 'lightred'))
                if qs1.lower() == 'y' or qs1.lower() == 'yes':
                    return self.download(url, dtype, pcloud, agl, download_path, provider, provider_quality, all_download)
                elif qs1.lower() == 'a' or qs1.lower() == 'auto':
                    nt = 1
                    while 1:
                        if downloading == "Link Dead! or Host is temporarily down! Generate again after 5 minutes!" or not downloading:
                            downloading = self.agl.generate(download_provider_url, True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
                            debug(downloading=downloading)
                            nt += 1
                            sys.stdout.write('#')
                            if nt == cmdw.getWidth():
                                break
                        else:
                            nt = (cmdw.getWidth() - nt)
                            sys.stdout.write('#' * (nt - 1))
                            break

        # return self.navigator(pcloud, download_path)

    def download_commas(self, list_commas, all_episode, download_path=os.getcwd(), pcloud=False, use_proxy=False):
        debug()
        for i in list_commas:
            if str(i).strip() == '':
                dlist.remove(i)
        qs3 = raw_input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
        qs4 = raw_input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
        if not qs3:
            qs3 = 'zippyshare'
        if not qs4:
            qs4 = '480p'
        for i in list_commas:
            downloads, episodes, infos = self.get_anime_details(all_episode[int(i) - 1].get('url'))
            for d in downloads:
                if d.get('name').strip().lower() == qs3.lower() and qs4 in d.get('quality').lower():
                    # return self.download(all_episode[int(i) - 1].get('url'), 'anime', pcloud, download_path=download_path, provider=qs3, provider_quality=qs4)
                    debug(download_path=download_path)
                    print "download_path =", download_path
                    self.agl.generate(d.get('link'), True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)

    def download_alls(self, all_episode, download_path=os.getcwd(), pcloud=False, use_proxy=False, qs3 = None, qs4 = None):
        debug()
        if not qs3:
            qs3 = raw_input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
        if not qs4:
            qs4 = raw_input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
        if not len(qs3) > 2:
            qs3 = raw_input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
        if not len(qs4) > 2:
            qs4 = raw_input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
        if not qs3:
            qs3 = 'zippyshare'
        if not qs4:
            qs4 = '480p'
        debug(qs3 = qs3, debug = True)
        debug(qs4 = qs4, debug = True)
        debug(all_episode = all_episode, debug = True)
        for i in all_episode:
            downloads, episodes, infos = self.get_anime_details(i.get('url'))
            debug(downloads = downloads, debug = True)
            debug(episodes = episodes, debug = True)
            debug(infos = infos, debug = True)
            for d in downloads:
                if d.get('name').strip().lower() == qs3.lower() and qs4 in d.get('quality').lower():
                    generated = self.agl.generate(d.get('link'), True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
                    debug(generated = generated, debug = True)
                    if 'http' in generated:
                        pass
                    elif 'https' in generated:
                        pass
                    else:
                        if generated == False:
                            qs3 = raw_input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
                            qs4 = raw_input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
                            return self.download_alls(all_episode, download_path, pcloud, use_proxy, qs3, qs4)


    def print_info(self, infos, dtype='anime', pcloud=False):
        debug()
        len_limit = int(cmdw.getWidth() / 3)
        # sinopsis_split = textwrap.wrap(infos.get('sinopsis'))
        if dtype == 'anime':
            sinopsis_split = textwrap.wrap(infos.get('sinopsis'))
            print "Name      : ", make_colors(infos.get('name').encode('utf-8'), 'lightgreen')
            print "Episode   : ", make_colors(infos.get('episode').encode('utf-8'), 'lightred')
            if infos.get('season'):
                print "Season    : ", make_colors(infos.get('season').encode('utf-8'), 'lightblue')
            if infos.get('air_date'):
                print "Air Date  : ", make_colors(infos.get('air_date').encode('utf-8'), 'lightmagenta')
            if infos.get('source'):
                print "Source    : ", make_colors(infos.get('source').encode('utf-8'), 'lightwhite')
            print "Sinopsis  : ", make_colors(sinopsis_split[0].encode('utf-8'), 'lightyellow')
            if len(sinopsis_split) > 1:
                for i in sinopsis_split[1:]:
                    print "            ", make_colors(i.encode('utf-8'), 'lightyellow')
        if dtype == 'new_anime':
            sinopsis_split = textwrap.wrap(infos.get('sinopsis'))
            print "Name            : ", make_colors(infos.get('name').encode('utf-8'), 'lightgreen')
            print "Release         : ", make_colors(infos.get('release').get('year').encode('utf-8'), 'lightwhite')
            print "Type            : ", make_colors(infos.get('anime_type').encode('utf-8'), 'lightcyan')
            print "First Air Date  : ", make_colors(infos.get('first_air_date').encode('utf-8'), 'lightblue')
            print "Last Air Date   : ", make_colors(infos.get('last_air_date').encode('utf-8'), 'lightblue')
            print "Number Episode  : ", make_colors(infos.get('episode').encode('utf-8'), 'lightmagenta')
            print "Season          : ", make_colors(infos.get('season').encode('utf-8'), 'lightmagenta')
            print "Original Name   : ", make_colors(infos.get('jpname').encode('utf-8'), 'lightwhite')
            print "Status          : ", make_colors(infos.get('tv_status').encode('utf-8'), 'lightred')
            print "Sinopsis        : ", make_colors(sinopsis_split[0].encode('utf-8'), 'lightyellow')
            if len(sinopsis_split) > 1:
                for i in sinopsis_split[1:]:
                    print "                  ", make_colors(i.encode('utf-8'), 'lightyellow')

        if dtype == 'movie':
            description_split = textwrap.wrap(infos.get('description'))
            print "Name           : ", make_colors(infos.get('name').encode('utf-8'), 'lightgreen')
            print "Date           : ", make_colors(infos.get('date').encode('utf-8'), 'lightblue')
            print "Original Name  : ", make_colors(infos.get('jpname').encode('utf-8'), 'lightwhite')
            print "IMDb           : ", make_colors(infos.get('imdb').encode('utf-8'), 'lightmagenta')
            if description_split:
                print "Description    : ", make_colors(description_split[0].encode('utf-8'), 'lightyellow')
                if len(description_split) > 1:
                    for i in description_split[1:]:
                        print "                 ", make_colors(i.encode('utf-8'), 'lightyellow')

    def print_episodes(self, episodes, pcloud=False, download_path=os.getcwd(), refresh=False, print_list=False):
        debug()
        colors_choice = ['lightgreen', 'lightcyan', 'lightwhite', 'lightyellow']
        list_episodes_edit = []
        for i in episodes:
            # print str(episodes.index(i) + 1) + ". " + make_colors(i.get('name'), 'black', random.choice(colors_choice))
            list_episodes_edit.append(str(episodes.index(i) + 1) + ". " + make_colors(i.get('name'), 'lightred', random.choice(colors_choice)))
        self.makeList(list_episodes_edit, 3)

    def downloadImage(self, list_images, use_proxy=False):
        debug()
        debug(use_proxy=use_proxy)
        downloadPath = os.path.join(os.getenv('TEMP'), 'neonime', 'images')
        image_downloaded = []
        if not os.path.isdir(downloadPath):
            os.makedirs(downloadPath)

        for i in list_images:
            if i:
                # print "downloadImage -> i :", i
                while 1:
                    try:
                        if use_proxy:
                            r = requests.get(i, stream = True, proxies=self.proxies)
                        else:
                            r = requests.get(i, stream = True)
                        #print "\n"
                        break
                    except:
                        sys.stdout.write(".")
                        time.sleep(3)
                # print "\n"

                from PIL import Image
                from StringIO import StringIO
                img = Image.open(StringIO(r.content))
                img_type = mimelist.get2(img.format)[1]
                #print "savePoster -> name 1 =", name
                if os.path.splitext(os.path.basename(i))[1] == None:
                    name = os.path.splitext(os.path.basename(i))[1] + "." + img_type
                    #print "savePoster -> name 2 =", name
                else:
                    name = os.path.basename(i)

                f = open(os.path.join(downloadPath, name), 'wb')
                img.save(f)
                f.close()
                image_downloaded.append(os.path.join(downloadPath, name))
        return image_downloaded

    def downloadAllLists(self, dlist, update_anime_range="", new_anime_range="", new_movies_range="", data_episode=None, pcloud=False, download_path=os.getcwd(), refresh=False, print_list=True, qs=None, search=False, download_all_episode=False, data_pages=None, use_proxy=False):
        debug()
        dtype = 'anime'
        update_anime = self.update_anime[0]
        new_anime = self.new_anime[0]
        new_movies = self.new_movies[0]
        qs3 = raw_input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
        qs4 = raw_input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
        if not qs3:
            qs3 = 'mega'
        if not qs4:
            qs4 = '480p'
        if data_episode and search:  # search_result => data_episode
            for i in data_episode:
                if 'movie' in i.get('name').lower() or 'movie' in i.get('season').lower():
                    dtype = 'movie'
                elif 'ona' in i.get('name').lower() or 'ona' in i.get('season').lower():
                    dtype = 'movie'
                elif 'ova' in i.get('name').lower() or 'ova' in i.get('season').lower():
                    dtype = 'movie'
                self.download(i.get('url'), dtype, pcloud, download_path = download_path, provider= qs3, provider_quality= qs4, use_proxy = use_proxy)
        else:
            for i in dlist:
                if int(i) in update_anime_range:
                    url_selected = update_anime[update_anime_range.index(int(i))].get('url')
                elif int(i) in new_anime_range:
                    url_selected = new_anime[new_anime_range.index(int(i))].get('url')
                elif int(i) in new_movies_range:
                    url_selected = new_movies[new_movies_range.index(int(i))].get('url')
                if '/episode/' in url_selected:
                    if data_episode:
                        if not int(i) > len(data_episode):
                            url_selected = data_episode[int(i)-1].get('url')
                            debug(url_selected=url_selected)
                        else:
                            print make_colors("invalid episode number", 'lightwhite', 'lightred')
                            debug(RETURN=False)
                            return False

                    self.download(url_selected, 'anime', pcloud, download_path=download_path, provider=qs3, provider_quality=qs4, use_proxy=use_proxy)
                elif '/tvshows/' in url_selected:
                    if not data_episode:
                        all_episode, infos = self.get_new_anime_details(url_selected)
                        for i in all_episode:
                            print str(all_episode.index(i) + 1) + ". " + make_colors(i.get('name'), 'lightgreen') + " (" + make_colors(i.get('number'), 'black', 'lightyellow') + ") [" + make_colors(i.get('date'), 'lightwhite', 'lightmagenta') + "]"
                    else:
                        all_episode = data_episode
                    qs = raw_input("select Number to Download or option: ")
                    url_selected = all_episode[int(qs) - 1].get('url')
                    print make_colors("URL", 'lw', 'lm') + ": " + make_colors(url_selected, 'lg')
                    self.download(url_selected, 'anime', pcloud, download_path=download_path, provider=qs3, provider_quality=qs4, use_proxy=use_proxy)
                else:
                    print make_colors("DOWNLOAD URL", 'lw', 'lm') + ": " + make_colors(url_selected, 'lg')
                    self.download(url_selected, 'movie', pcloud, download_path=download_path, provider=qs3, provider_quality=qs4, use_proxy=use_proxy)

    def dlist_parser(self, qs1):
        debug()
        dlist = []
        if "," in str(qs1).strip():
            dlist = re.sub(" ", "", str(qs1).strip())
            dlist = re.split(",", str(qs1).strip())
            for l in dlist:
                if "-" in l:
                    l = re.split("-", str(qs1).strip())
                    l = range(int(l[0]),int(l[1])+1)
                    for r in l:
                        dlist.append(str(r))
            dlist = sorted(set(dlist))
            debug(dlist=dlist)

        elif "-" in str(qs1).strip():
            dlist = []
            dlist_pre = re.sub(" ", "", str(qs1).strip())
            dlist_pre = re.split("-", str(qs1).strip(), 1)
            dlist_pre = range(int(dlist_pre[0]), int(dlist_pre[1]) + 1)
            for l in dlist_pre:
                dlist.append(str(l))
            debug(dlist=dlist)
            debug(dlist=dlist)
        return dlist

    def navigator(self, pcloud=False, download_path=os.getcwd(), refresh=False, print_list=True, data_episode=None, qs=None, url_selected=None, search=False, download_all_episode=False, data_pages=None, home_url=None, debugx=False, use_proxy=False, code_action=None):
        debug()
        if debugx:
            os.environ.update({'DEBUG':'1'})
        debug(qs=qs)
        debug(home_url=home_url)
        if not data_episode:
            if hasattr(self, "update_anime") and hasattr(self, "new_anime") and hasattr(self, "new_movies"):
                if refresh:
                    self.home(home_url)
                else:
                    pass
            else:
                self.home(home_url)
        if home_url and not search:
            self.home(home_url)
        # else:
        #     self.print_episodes(data_episode)
        number = 0
        update_anime_range = []
        new_anime_range = []
        new_movies_range = []
        print "\n"
        debug(hasattr_update_anime=hasattr(self, "update_anime"))
        if hasattr(self, "update_anime"):
            if print_list:
                print make_colors("Update Animes:", 'black', 'lightgreen')
            update_anime = self.update_anime[0]
            debug(update_anime=update_anime)
            for i in update_anime:
                number = update_anime.index(i)
                if len(str(number)) == 1 and not number == 9:
                    number = "0" + str(number + 1)
                else:
                    number = str(number + 1)
                update_anime_range.append(int(number))
                if print_list:
                    print " " * 4 + number + ".", make_colors(i.get('name').encode('utf-8'), 'lightgreen') + " [" + make_colors(str(i.get('episode').encode('utf-8')), 'black', 'lightcyan') + "/" + make_colors(i.get('season').encode('utf-8'), 'lightwhite', 'lightmagenta') + "] "

        if hasattr(self, "new_anime"):
            if print_list:
                print make_colors("New Animes:", 'black', 'lightyellow')
            new_anime = self.new_anime[0]
            debug(new_anime=new_anime)
            for i in new_anime:
                number = int(number)
                if len(str(number)) == 1 and not number == 9:
                    number = "0" + str(number + 1)
                else:
                    number = str(number + 1)
                new_anime_range.append(int(number))
                if print_list:
                    print " " * 4 + number + ".", make_colors(i.get('name').encode('utf-8'), 'lightyellow') + " [" + make_colors(str(i.get('year')), 'black', 'lightcyan') + "] "

        if hasattr(self, "new_movies"):
            if print_list:
                print make_colors("New Movies:", 'lightwhite', 'lightmagenta')
            new_movies = self.new_movies[0]
            debug(new_movies=new_movies)
            for i in new_movies:
                number = int(number)
                if len(str(number)) == 1 and not number == 9:
                    number = "0" + str(number + 1)
                else:
                    number = str(number + 1)
                new_movies_range.append(int(number))
                if print_list:
                    print " " * 4 + number + ".", make_colors(i.get('name').encode('utf-8'), 'lightmagenta') + " [" + make_colors(str(i.get('year')), 'black', 'lightcyan') + "] "
        print "\n"
        qnote = "[" + str(PID) + "]" + make_colors("Format Selecting:", 'black', 'lightyellow') + " " + make_colors("number", 'lightwhite', 'lightred') + "[" + make_colors("i", 'black', 'lightcyan') + "|" + make_colors("t", 'lightwhite', 'lightblue') + "|" + make_colors("d", 'black', 'lightgreen') + "|" + make_colors("D", 'black', 'lightgreen') + "|" + make_colors("e", 'lightwhite', 'lightmagenta') + "|" + make_colors("r", 'lightred', 'lightwhite') + "|" + make_colors("s", 'lightwhite', 'lightred') + "]\n" + make_colors("i = info", 'black', 'lightcyan') + ", " + make_colors("t = thumb/images", 'lightwhite', 'lightblue') + ", " + make_colors("d = download", 'black', 'lightgreen') + ", " + make_colors("D = download path", 'black', 'lightgreen') + ", " + make_colors("e = episode", 'lightwhite', 'lightmagenta') + ", " + make_colors("r = refresh", 'lightred', 'lightwhite') + ", " + make_colors("s = search", 'lightwhite', 'lightred') + " \n" + make_colors("Select Number: ", 'black', 'lightyellow')

        qnote1 = "[" + str(PID) + "]" + make_colors("Format Selecting:", 'black', 'lightyellow') + " " + make_colors("number", 'lightwhite', 'lightred') + "[" + make_colors("i", 'black', 'lightcyan') + "|" + make_colors("t", 'lightwhite', 'lightblue') + "|" + make_colors("d", 'black', 'lightgreen') + "|" + make_colors("D", 'black', 'lightgreen') + "|" + make_colors("e", 'lightwhite', 'lightmagenta') + "|" + make_colors("r", 'lightred', 'lightwhite') + "|" + make_colors("s", 'lightwhite', 'lightred') + "|" + make_colors("a", 'lightwhite', 'lightred') + "]\n" + make_colors("Format Selected Number:", 'black', 'lightyellow') + " " + make_colors('(number1, number2), (first_number-last_number)', 'red', 'lightwhite') + "\n" + make_colors("i = info", 'black', 'lightcyan') + ", " + make_colors("t = thumb/images", 'lightwhite', 'lightblue') + ", " + make_colors("d = download", 'black', 'lightgreen') + ", " + make_colors("D = download path", 'black', 'lightgreen') + ", " + make_colors("e = episode", 'lightwhite', 'lightmagenta') + ", " + make_colors("a = all (download all)", 'lightwhite', 'lightred') + " \n" + make_colors("Select Number: ", 'black', 'lightyellow')

        qnote2 = "[" + str(PID) + "]" + make_colors("Format Selecting:", 'black', 'lightyellow') + " " + make_colors("number", 'lightwhite', 'lightred') + "[" + make_colors("i", 'black', 'lightcyan') + "|" + make_colors("t", 'lightwhite', 'lightblue') + "|" + make_colors("d", 'black', 'lightgreen') + "|" + make_colors("D", 'black', 'lightgreen') + "|" + make_colors("e", 'lightwhite', 'lightmagenta') + "|" + make_colors("r", 'lightred', 'lightwhite') + "]\n" + make_colors("i = info", 'black', 'lightcyan') + ", " + make_colors("t = thumb/images", 'lightwhite', 'lightblue') + ", " + make_colors("d = download", 'black', 'lightgreen') + ", " + make_colors("D = download path", 'black', 'lightgreen') + ", " + make_colors("e = episode", 'lightwhite', 'lightmagenta') + ", " + make_colors("r = refresh", 'lightred', 'lightwhite') + " \n" + make_colors("Select Number: ", 'black', 'lightyellow')

        qnote3 = "[" + str(PID) + "]" + make_colors("Format Selecting:", 'black', 'lightyellow') + " " + make_colors("number", 'lightwhite', 'lightred') + "[" + make_colors("i", 'black', 'lightcyan') + "|" + make_colors("t", 'lightwhite', 'lightblue') + "|" + make_colors("d", 'black', 'lightgreen') + "|" + make_colors("D", 'black', 'lightgreen') + "|" + make_colors("e", 'lightwhite', 'lightmagenta') + "|" + make_colors("r", 'lightred', 'lightwhite') + "|" + make_colors("s", 'lightwhite', 'lightred') + "|" + make_colors("a", 'lightwhite', 'lightred') + "|" + make_colors("p", 'lightwhite', 'lightgreen') + "]\n" + make_colors("Format Selected Number:", 'black', 'lightyellow') + " " + make_colors('(number1, number2), (first_number-last_number)', 'red', 'lightwhite') + "\n" + make_colors("i = info", 'black', 'lightcyan') + ", " + make_colors("t = thumb/images", 'lightwhite', 'lightblue') + ", " + make_colors("d = download", 'black', 'lightgreen') + ", " + make_colors("D = download path", 'black', 'lightgreen') + ", " + make_colors("e = episode", 'lightwhite', 'lightmagenta') + ", " + make_colors("a = all (download all)", 'lightwhite', 'lightred') + ", " + make_colors("s = search", 'lightwhite', 'lightred') + ", " + make_colors("p = page", 'black', 'lightgreen') + " \n" + make_colors("Select Number: ", 'black', 'lightyellow')

        qnote4 = "[" + str(PID) + "]" + make_colors("Format Selecting:", 'black', 'lightyellow') + " " + make_colors("number", 'lightwhite', 'lightred') + "[" + make_colors("i", 'black', 'lightcyan') + "|" + make_colors("t", 'lightwhite', 'lightblue') + "|" + make_colors("d", 'black', 'lightgreen') + "|" + make_colors("D", 'black', 'lightgreen') + "|" + make_colors("e", 'lightwhite', 'lightmagenta') + "|" + make_colors("r", 'lightred', 'lightwhite') + "|" + make_colors("s", 'lightwhite', 'lightred') + "|" + make_colors("a", 'lightwhite', 'lightred') + "|" + make_colors("p", 'lightwhite', 'lightgreen') + "]\n" + make_colors("Format Selected Number:", 'black', 'lightyellow') + " " + make_colors('(number1, number2), (first_number-last_number)', 'red', 'lightwhite') + "\n" + make_colors("i = info", 'black', 'lightcyan') + ", " + make_colors("t = thumb/images", 'lightwhite', 'lightblue') + ", " + make_colors("d = download", 'black', 'lightgreen') + ", " + make_colors("D = download path", 'black', 'lightgreen') + ", " + make_colors("e = episode", 'lightwhite', 'lightmagenta') + ", " + make_colors("a = all (download all)", 'lightwhite', 'lightred') + ", " + make_colors("s = search", 'lightwhite', 'lightred') + ", " + make_colors("p = page", 'black', 'lightgreen') + ": "

        if not qs:
            qs1 = raw_input(qnote3)
        else:
            qs1 = qs
        debug(qs1=qs1)
        # print "qs1 0 =", qs1
        # print "url_selected =", url_selected
        # print "data_episode =", data_episode
        if qs1:
            debug(qs1=qs1, debug = True)
            if str(qs1).strip() == 'x' or str(qs1).strip() == 'q' or str(qs1).strip() == 'exit' or str(qs1).strip() == 'quit':
                sys.exit(0)
            if str(qs1).strip().isdigit():
                debug("str(qs1).strip().isdigit()")
                debug(data_episode=data_episode)
                debug(url_selected=url_selected)
                if not data_episode:
                    if not url_selected:
                        if int(qs1) in update_anime_range:
                            url_selected = update_anime[update_anime_range.index(int(qs1))].get('url')
                        elif int(qs1) in new_anime_range:
                            url_selected = new_anime[new_anime_range.index(int(qs1))].get('url')
                        elif int(qs1) in new_movies_range:
                            url_selected = new_movies[new_movies_range.index(int(qs1))].get('url')


                    if '/episode/' in url_selected:
                        self.download(url_selected, 'anime', pcloud, download_path=download_path, use_proxy=use_proxy)
                    elif '/tvshows/' in url_selected:
                        if not data_episode:
                            all_episode, infos = self.get_new_anime_details(url_selected)
                            for i in all_episode:
                                print str(all_episode.index(i) + 1) + ". " + make_colors(i.get('name'), 'lightgreen') + " (" + make_colors(i.get('number'), 'black', 'lightyellow') + ") [" + make_colors(i.get('date'), 'lightwhite', 'lightmagenta') + "]"
                        else:
                            all_episode = data_episode
                        qs = raw_input(make_colors("Select Number: ", 'black', 'lightcyan'))
                        return self.navigator(pcloud, download_path, refresh, False, all_episode, qs, None, False, False, None, None, debugx, use_proxy)
                    else:
                        return self.download(url_selected, 'movie', pcloud, download_path=download_path, use_proxy=use_proxy)
                else:
                    if not url_selected:
                        # qs2 = raw_input(qnote1)
                        if str(qs1).strip().isdigit():
                            self.download(data_episode[int(qs1) - 1].get('url'), 'anime', pcloud, download_path=download_path, use_proxy=use_proxy)
                        elif "-" in str(qs1).strip() or "," in str(qs1).strip():
                            dlist = self.dlist_parser(qs1)
                        elif "a" == str(qs1).strip().lower():
                            self.download_alls(data_episode, download_path, pcloud, use_proxy)
                        if dlist:
                            self.download_commas(dlist, data_episode, download_path, pcloud, use_proxy)
                    else:
                        if '/episode/' in url_selected:
                            self.download(url_selected, 'anime', pcloud, download_path=download_path, use_proxy=use_proxy)
                        elif '/tvshows/' in url_selected:
                            if not data_episode:
                                all_episode, infos = self.get_new_anime_details(url_selected)
                                for i in all_episode:
                                    print str(all_episode.index(i) + 1) + ". " + make_colors(i.get('name'), 'lightgreen') + " (" + make_colors(i.get('number'), 'black', 'lightyellow') + ") [" + make_colors(i.get('date'), 'lightwhite', 'lightmagenta') + "]"
                            else:
                                all_episode = data_episode
                            qs = raw_input(make_colors("Select Number: ", 'black', 'lightcyan'))
                            return self.navigator(pcloud, download_path, refresh, False, all_episode, qs, None, search, False, None, None, debugx, use_proxy=use_proxy)
                        else:
                            return self.download(url_selected, 'movie', pcloud, download_path=download_path, use_proxy=use_proxy)
                        if search:
                            return self.navigator(pcloud, download_path, refresh, False, search=True, data_pages=data_pages, use_proxy=use_proxy)

            else:
                debug("NOT DIGIT !", debug = True)
                if "-" in str(qs1).strip() and str(qs1)[str(qs1).index("-") - 1].isdigit() or "," in str(qs1).strip():
                    dlist = self.dlist_parser(qs1)
                    self.downloadAllLists(dlist, update_anime_range, new_anime_range, new_movies_range, data_episode, pcloud, download_path, refresh, print_list, qs, search, download_all_episode, data_pages, use_proxy)
                elif "a" == str(qs1).strip().lower():
                    debug("qs == 'a'", debug = True)
                    dlist = update_anime_range + new_anime_range + new_movies_range
                    debug(dlist = dlist, debug = True)
                    debug(data_episode = data_episode, debug = True)
                    #self.downloadAllLists(dlist, update_anime_range, new_anime_range, new_movies_range, data_episode, pcloud, download_path, refresh, print_list, qs, search, download_all_episode, data_pages, use_proxy)
                    self.download_alls(data_episode, download_path, pcloud, use_proxy)

                else:
                    debug(url_selected=url_selected)
                    if url_selected and not search:
                        if '/episode/' in url_selected:
                            self.download(url_selected, 'anime', pcloud, download_path=download_path, use_proxy=use_proxy)
                        elif '/tvshows/' in url_selected:
                            if not data_episode:
                                all_episode, infos = self.get_new_anime_details(url_selected)
                                for i in all_episode:
                                    print str(all_episode.index(i) + 1) + ". " + make_colors(i.get('name'), 'lightgreen') + " (" + make_colors(i.get('number'), 'black', 'lightyellow') + ") [" + make_colors(i.get('date'), 'lightwhite', 'lightmagenta') + "]"
                            else:
                                all_episode = data_episode
                            qs = raw_input(make_colors("Select Number: ", 'black', 'lightcyan'))
                            return self.navigator(pcloud, download_path, refresh, False, all_episode, qs, None, False, False, None, None, debugx, use_proxy=use_proxy)
                        else:
                            return self.download(url_selected, 'movie', pcloud, download_path=download_path, use_proxy=use_proxy)
                    else:
                        list_selected_code = ['r', 'd', 'i', 't', 'e', 's', 'p']
                        list_code = ""
                        list_code_print = ""
                        qs1_isdigit = ''
                        check_i = str(qs1).strip()
                        if len(check_i) > 1:
                            debug("len(check_i) > 1")
                            if check_i[-1] in list_selected_code:
                                qs1_isdigit = check_i[0:-1]
                                debug(qs1_isdigit=qs1_isdigit)
                                list_code = check_i[-1]
                                debug(list_code=list_code)
                            else:
                                qs_pass = raw_input(make_colors("Press Enter to Continue, e[x]it|[q]uit = exit: ", 'lightwhite', 'lightred'))
                                if qs_pass == 'x' or qs_pass == 'q' or qs_pass == 'exit' or qs_pass == 'quit':
                                    print make_colors('Bye .... :)', 'lightred', attrs=['blink'])
                                    sys.exit(0)
                                else:
                                    return self.navigator(pcloud, download_path, refresh, use_proxy=use_proxy)

                        else:
                            list_code = str(qs1).strip()
                            debug(list_code=list_code)
                            if list_code == 'i':
                                list_code_print = 'Info'
                            elif list_code == 'e':
                                list_code_print = 'Episode'
                            elif list_code == 'd':
                                list_code_print = 'Download'
                            elif list_code == 'D':
                                list_code_print = 'Download Path'
                            elif list_code == 't':
                                list_code_print = 'Thumb'
                            elif list_code == 's':
                                list_code_print = 'Search'
                            elif list_code == 'p':
                                list_code_print = "Page"
                            elif list_code == 'r':
                                list_code_print = "Refresh"
                            else:
                                qs_pass = raw_input(make_colors("Press Enter to Continue, e[x]it|[q]uit = exit: ", 'lightwhite', 'lightred'))
                                if qs_pass == 'x' or qs_pass == 'q' or qs_pass == 'exit' or qs_pass == 'quit':
                                    print make_colors('Bye .... :)', 'lightred', attrs=['blink'])
                                    sys.exit(0)
                                else:
                                    return self.navigator(pcloud, download_path, refresh)
                        if not url_selected:
                            if not list_code == 's' and not list_code == 'p' and not list_code == 'r' and not list_code == 'D':
                                if int(qs1_isdigit) in update_anime_range:
                                    url_selected = update_anime[update_anime_range.index(int(qs1_isdigit))].get('url')
                                elif int(qs1_isdigit) in new_anime_range:
                                    url_selected = new_anime[new_anime_range.index(int(qs1_isdigit))].get('url')
                                elif int(qs1_isdigit) in new_movies_range:
                                    url_selected = new_movies[new_movies_range.index(int(qs1_isdigit))].get('url')

                        if list_code == 'r':
                            if not data_episode:
                                self.home()
                            return self.navigator(pcloud, download_path, refresh, print_list, data_episode, use_proxy=use_proxy)

                        elif list_code == 'D':
                            global DOWNLOAD_PATH
                            DOWNLOAD_PATH = raw_input('Set DOWNLOAD_PATH: ')
                            while 1:
                                if os.path.isdir(DOWNLOAD_PATH):
                                    break
                                else:
                                    DOWNLOAD_PATH = raw_input('Set DOWNLOAD_PATH: ')

                            os.environ.update({'DOWNLOAD_PATH':DOWNLOAD_PATH})
                            download_path = DOWNLOAD_PATH

                            return self.navigator(pcloud, download_path, refresh, print_list, data_episode, qs, url_selected, search, download_all_episode, data_pages, home_url, debugx, use_proxy=use_proxy)

                        elif list_code == "d":
                            return self.navigator(pcloud, download_path, refresh, False, data_episode, qs1_isdigit, url_selected, search, download_all_episode, data_pages, home_url, debugx, use_proxy)

                        elif list_code == 'i':
                            if qs1_isdigit:
                                if not data_episode:
                                    info_exist = False
                                    if '/episode/' in url_selected:
                                        all_download, all_episode, infos = self.get_anime_details(update_anime[update_anime_range.index(int(qs1_isdigit))].get('url'))
                                        self.print_info(infos)
                                        info_exist = True
                                    elif '/tvshows/' in url_selected:
                                        all_episode, infos = self.get_new_anime_details(url_selected)
                                        self.print_info(infos, 'new_anime')
                                        info_exist = True
                                    else:
                                        all_download, infos = self.get_movie_details(url_selected)
                                        self.print_info(infos, 'movie')
                                        info_exist = True
                                    if not info_exist:
                                        print make_colors('No Infos', 'lightwhite', 'lightred')
                                        # return self.navigator(pcloud, download_path, refresh, False)
                                else:
                                    all_download, all_episode, infos = self.get_anime_details(data_episode[int(qs1_isdigit) - 1].get('url'))
                                    self.print_info(infos)

                        elif list_code == 't':
                            import tkimage
                            # pool = ThreadPool(processes= 100)
                            # imgview = tkimage.Application()
                            if qs1_isdigit:
                                if not data_episode:
                                    if '/episode/' in url_selected:
                                        all_download, all_episode, infos = self.get_anime_details(url_selected)
                                        # print "infos =", infos
                                        image_to_download = [infos.get('poster'), infos.get('thumb')]
                                        if infos.get('backdrops'):
                                            if not infos.get('backdrops') == infos.get('thumb'):
                                                image_to_download = [infos.get('poster'), infos.get('thumb'), infos.get('backdrops')]
                                        imgs = self.downloadImage(image_to_download, use_proxy=use_proxy)
                                        imgs.insert(0, 'Neonime: %s, n = Next'%(infos.get('name')))
                                        args = tuple(imgs)
                                        tx = Process(target=tkimage.showImages, args=args)
                                        tx.start()
                                        qt_selected = None
                                        self.print_info(infos)
                                        qt = raw_input(qnote4)
                                        if len(qt) == 1:
                                            if not str(qt).isdigit():
                                                qt_selected = qs1_isdigit + qt
                                            else:
                                                qt_selected = qt
                                        else:
                                            if qt and not str(qt).strip() == '':
                                                if not str(qt[-1]).isdigit() and str(qt[:-1]).isdigit():
                                                    qt_selected = qt
                                                else:
                                                    pass
                                        print_list_t = True
                                        if len(qt) > 1:
                                            if qt[-1] == 'd':
                                                print_list_t = False

                                        debug(qt_selected=qt_selected)
                                        return self.navigator(pcloud, download_path, refresh, print_list_t, data_episode, qt_selected, None, search, download_all_episode, data_pages, home_url, debugx, use_proxy)
                                    elif '/tvshows/' in url_selected:
                                        all_episode, infos = self.get_new_anime_details(new_anime[new_anime_range.index(int(qs1_isdigit))].get('url'))
                                        # print "infos =", infos
                                        image_to_download = [infos.get('poster'), infos.get('thumb')]
                                        if infos.get('backdrops'):
                                            if not infos.get('backdrops') == infos.get('thumb'):
                                                image_to_download = [infos.get('poster'), infos.get('thumb'), infos.get('backdrops')]

                                        imgs = self.downloadImage(image_to_download)
                                        imgs.insert(0, 'Neonime: %s, n = Next'%(infos.get('name')))
                                        args = tuple(imgs)
                                        # tx = pool.apply_async(tkimage.showImages, args)
                                        tx = Process(target=tkimage.showImages, args=args)
                                        tx.start()
                                        self.print_info(infos, 'new_anime')
                                        qt_selected = None
                                        qt = raw_input(qnote4)
                                        if len(qt) == 1:
                                            if not str(qt).isdigit():
                                                qt_selected = qs1_isdigit + qt
                                            else:
                                                qt_selected = qt
                                        else:
                                            if qt:
                                                if not str(qt[-1]).isdigit() and str(qt[:-1]).isdigit():
                                                    qt_selected = qt
                                                else:
                                                    pass

                                        if qt[-1] == 'd':
                                            print_list_t = False
                                        else:
                                            print_list_t = True
                                        debug(qt_selected=qt_selected)
                                        return self.navigator(pcloud, download_path, refresh, print_list_t, data_episode, qt_selected, None, search, download_all_episode, data_pages, home_url, debugx, use_proxy)
                                    elif int(qs1_isdigit) in new_movies_range:
                                        all_download, infos = self.get_movie_details(new_movies[new_movies_range.index(int(qs1_isdigit))].get('url'))
                                        # print "infos =", infos
                                        image_to_download = [infos.get('poster'), infos.get('screenshot')]
                                        if infos.get('backdrops'):
                                            if not infos.get('backdrops') == infos.get('thumb'):
                                                image_to_download = [infos.get('poster'), infos.get('thumb'), infos.get('backdrops')]

                                        imgs = self.downloadImage(image_to_download, use_proxy=use_proxy)
                                        imgs.insert(0, 'Neonime: %s, n = Next'%(infos.get('name')))
                                        args = tuple(imgs)
                                        # tx = pool.apply_async(tkimage.showImages, args)
                                        tx = Process(target=tkimage.showImages, args=args)
                                        tx.start()
                                        self.print_info(infos, 'movie')
                                        qt_selected = None
                                        qt = raw_input(qnote4)
                                        if len(qt) == 1:
                                            if not str(qt).isdigit():
                                                qt_selected = qs1_isdigit + qt
                                            else:
                                                qt_selected = qt
                                        else:
                                            if qt:
                                                if not str(qt[-1]).isdigit() and str(qt[:-1]).isdigit():
                                                    qt_selected = qt
                                                else:
                                                    pass

                                        if qt[-1] == 'd':
                                            print_list_t = False
                                        else:
                                            print_list_t = True
                                        debug(qt_selected=qt_selected)
                                        return self.navigator(pcloud, download_path, refresh, print_list_t, data_episode, qt_selected, None, search, download_all_episode, data_pages, home_url, debugx, use_proxy)
                                    else:
                                        print make_colors('No Infos', 'lightwhite', 'lightred')
                                        return self.navigator(pcloud, download_path, refresh, False, use_proxy=use_proxy)
                                else:
                                    all_download, all_episode, infos = self.get_anime_details(data_episode[int(qs1_isdigit) - 1].get('url'))
                                    # print "infos =", infos
                                    image_to_download = [infos.get('poster'), infos.get('thumb')]
                                    if infos.get('backdrops'):
                                        if not infos.get('backdrops') == infos.get('thumb'):
                                            image_to_download = [infos.get('poster'), infos.get('thumb'), infos.get('backdrops')]

                                    imgs = self.downloadImage(image_to_download, use_proxy=use_proxy)
                                    imgs.insert(0, 'Neonime: %s, n = Next'%(infos.get('name')))
                                    args = tuple(imgs)
                                    # tx = pool.apply_async(tkimage.showImages, args)
                                    tx = Process(target=tkimage.showImages, args=args)
                                    tx.start()
                                    self.print_info(infos)

                        elif list_code == 'e':
                            debug(url_selected=url_selected)
                            if qs1_isdigit:
                                if url_selected:
                                    if '/episode/' in url_selected:
                                        all_download, all_episode, infos = self.get_anime_details(update_anime[update_anime_range.index(int(qs1_isdigit))].get('url'))
                                        self.print_episodes(all_episode, pcloud, download_path, refresh, print_list=False)
                                    elif '/tvshows/' in url_selected:
                                        all_episode, infos = self.get_new_anime_details(new_anime[new_anime_range.index(int(qs1_isdigit))].get('url'))
                                        self.print_episodes(all_episode, pcloud, download_path, refresh, print_list=False)
                                    else:
                                        try:
                                            all_download, infos = self.get_movie_details(new_movies[new_movies_range.index(int(qs1_isdigit))].get('url'))
                                            self.print_info(infos, 'movie')
                                        except:
                                            print make_colors('No Episode', 'lightwhite', 'lightred')
                                            # return self.navigator(pcloud, download_path, refresh, False)
                                else:
                                    pass

                                return self.navigator(pcloud, download_path, refresh, False, all_episode, url_selected=url_selected, use_proxy=use_proxy)

                        elif list_code == 's' or search:
                            global IS_SEARCH
                            IS_SEARCH = True
                            debug("search action", debug = True)
                            debug(data_episode = data_episode, debug = True)
                            debug(qs1_isdigit = qs1_isdigit, debug = True)
                            if qs1_isdigit:
                                SEARCH_QUERY = qs1_isdigit
                                if not data_episode:
                                    if url_selected:
                                        search_result, pages = self.search(qs1_isdigit, search_url=url_selected)
                                    else:
                                        search_result, pages = self.search(qs1_isdigit)
                                else:
                                    debug(search_result = search_result, debug = True)
                                    search_result = data_episode
                                debug(search_result=search_result, debug = True)
                                list_result = []
                                for i in search_result:
                                    name = str(search_result.index(i) + 1) + ". " + i.get('name')
                                    if i.get('season') and i.get('episode'):
                                        name += " [" + i.get('season') + "/" + i.get('episode') + "]"
                                    elif i.get('season'):
                                        name += " [" + i.get('season') + "]"
                                    elif i.get('episode'):
                                        name += " [" + i.get('episode') + "]"
                                    list_result.append(name)
                                debug(list_result=list_result, debug = True)
                                self.makeList(list_result, 3)
                                debug(search=search, debug = True)
                                debug(IS_SEARCH=IS_SEARCH, debug = True)
                                if pages.get('last_page'):
                                    print make_colors("Number of Page: ", 'lightwhite', 'lightcyan') + make_colors(urlparse(pages.get('last_page')).path[-2], 'lightwhite', 'lightmagenta')
                                debug("print qnote3", debug = True)
                                qs2 = raw_input(qnote3)
                                if str(qs2).strip().isdigit():
                                    url_selected = search_result[int(qs2) - 1].get('url')
                                    debug(url_selected=url_selected)
                                    return self.navigator(pcloud, download_path, refresh, False, search_result, qs2, url_selected, True, data_pages=pages, use_proxy=use_proxy)
                                    # navigator(self, pcloud=False, download_path=os.getcwd(), refresh=False, print_list=True, data_episode=None, qs=None, url_selected=None, search=False, download_all_episode=False, data_pages=None)
                                else:
                                    if qs2 == 'x' or qs2 == 'q' or qs2 == 'exit' or qs2 == 'quit':
                                        print make_colors('Bye .... :)', 'lightred', attrs=['blink'])
                                        sys.exit(0)
                                    debug(data_pages=pages)
                                    debug(qs1=qs1)
                                    # url_selected = search_result[int(qs1_isdigit) - 1].get('url')
                                    # debug(url_selected=url_selected)
                                    return self.navigator(pcloud, download_path, refresh, False, search_result, search = True, data_pages=pages, qs=qs2, use_proxy=use_proxy)

                                # print "url_selected 1 =", url_selected
                                # return self.navigator(pcloud, download_path, refresh, False, data_episode, 0, url_selected)
                                return self.navigator(pcloud, download_path, refresh, False, search_result, qs2, url_selected, True, data_pages=pages, use_proxy=use_proxy)

                        elif list_code == 'p':
                            if IS_SEARCH:
                                search = True
                            page_url = ""
                            if search or data_pages:
                                pages = data_pages
                                debug(pages=pages, debug = True)
                            else:
                                pages = self.paginator(url=home_url)
                                debug(pages=pages, debug = True)
                            if isinstance(pages, dict):
                                debug("isinstance(pages, dict):", debug = True)
                                pages = pages.get(pages.keys()[-1])
                                debug(pages=pages, debug = True)

                            if qs1_isdigit:
                                debug("qs1_isdigit:", debug = True)
                                if qs1_isdigit == '1' or qs1_isdigit == 1:
                                    debug("qs1_isdigit == '1' or qs1_isdigit == 1:", debug = True)
                                    return self.navigator(pcloud, download_path, refresh, True, home_url=home_url, search=search, use_proxy=use_proxy)
                                else:
                                    for i in pages:
                                        if i.get(str(qs1_isdigit)):
                                            debug("i.get(str(qs1_isdigit)):", data = i.get(str(qs1_isdigit)))
                                            debug(i=i)
                                            debug(qs1_isdigit=qs1_isdigit)
                                            debug(i_get_qs1_isdigit=i.get(str(qs1_isdigit)))
                                            debug(qs1_isdigit=qs1_isdigit)
                                            debug(i_get_qs1_isdigit=i.get(str(qs1_isdigit)))
                                            page_url = i.get(str(qs1_isdigit))
                                            home_url = page_url
                                            debug(page_url=page_url)
                                            if search:
                                                return self.navigator(pcloud, download_path, refresh, False, url_selected=page_url, search=search, qs=qs1, data_pages=pages, use_proxy=use_proxy)
                                            debug("return for i in pages:", debug = True)
                                            return self.navigator(pcloud, download_path, refresh, True, home_url=page_url, search=search, data_pages=pages, use_proxy=use_proxy)

                            debug("return for no action", debug = True)
                            return self.navigator(pcloud, download_path, refresh, True, search=search, qs=qs1, home_url=home_url, data_pages=pages, use_proxy=use_proxy)

        qs_pass = raw_input(make_colors("Press Enter to Continue, e[x]it|[q]uit = exit: ", 'lightwhite', 'lightred'))
        if qs_pass == 'x' or qs_pass == 'q' or qs_pass == 'exit' or qs_pass == 'quit':
            print make_colors('Bye .... :)', 'lightred', attrs=['blink'])
            sys.exit(0)
        elif str(qs_pass).strip() == "":
            return self.navigator(pcloud, download_path, True)
        else:
            return self.navigator(pcloud, download_path, True, True, qs=qs)

    def navigator_search(self, query, pcloud=False, download_path=os.getcwd(), refresh=False):
        debug()

        pass

    def test(self):
        debug()
        import test

    def usage(self):
        debug()
        global DOWNLOAD_PATH
        import argparse
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-l', '--list', help='Browser Mode', action='store_true')
        parser.add_argument('-m', '--monitor', help='Realtime Monitoring update', action='store_true')
        parser.add_argument('-p', '--download-path', help='Download to', action='store', default=os.getcwd())
        parser.add_argument('--pcloud', help='Upload to Pcloud', action='store_true')
        parser.add_argument('-X', '--proxy', help='Use proxy, format: ip:port', action='store')
        parser.add_argument('-x', '--use-proxy', help='Use Auto proxy', action='store_true')
        parser.add_argument('-t', '--test', help='Run Test Script "test.py"', action='store_true')
        parser.add_argument('-P', '--page', help = 'Page of', action = 'store', type = str)

        # parser.add_argument('')
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            qs = None
            print_list = True
            if args.page:
                qs = args.page + 'p'
                print_list = False
            if args.proxy:
                if ":" in args.proxy:
                    proxy_ip, proxy_port = args.proxy.split(":")
                    self.setProxy(proxy_ip, proxy_port)
            else:
                proxy_ip = self.CONFIG.read_config('PROXY', 'address')
                proxy_port = self.CONFIG.read_config('PROXY', 'port')
                if proxy_ip and proxy_port:
                    self.setProxy(proxy_ip, proxy_port)
            if args.use_proxy:
                self.setProxy()
            if args.monitor:
                self.monitor(args.use_proxy)
            elif args.test:
                self.test()
            elif args.list:
                self.navigator(args.pcloud, args.download_path, use_proxy=args.use_proxy, qs = qs, print_list= print_list)
            else:
                self.navigator(args.pcloud, args.download_path, use_proxy=args.use_proxy, qs = qs, print_list= print_list)

if __name__ == '__main__':
    PID = os.getpid()
    print "PID:", PID
    c = Kusonime()
    c.home(debugx= True)
    #c.usage()

    #c.get_movie_details('https://neonime.org/ashita-sekai-ga-owaru-toshitemo-bd-subtitle-indonesia/')
    # print c.zippyshare_checker('https://www92.zippyshare.com/v/6UF65mOn/file.html')

    # c.home()
    #print c.get_batch_anime()
    #c.get_batch_detail("https://neonime.org/batch/ongaku-shoujo-tv-batch-subtitle-indonesia/")
    #c.search()
    #c.statistic()
    # c.monitor()
    #data = c.home()
    #for i in data:
        #print i
        #print "-" * 100
    # c.paginator(page_type='release')
    #c.get_anime_details()

