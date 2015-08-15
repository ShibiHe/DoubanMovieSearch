# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy_crawler.items import MovieItem
import re
import json

# This is a Douban Movie spider. It will get movie information from http://douban.movie.com.
# The information about a movie this spider will get is listed here:
#   Title Year Director Writer Actor Rating Introduction URL and some other information such as category, region.

# Spider will start crawling from START_URLS, for instance: START_URLS = ["http://douban.movie.com"].
# START_URLS is a list.

# Spider will load visited links first, those links will not be visited and crawled.
# Visited link file's name is in this format: "visited_linksXXX.json" XXX is "First", "Second"..."Seventh".
# Visited link file is a JSON file.
# This is my first python program, so a ungraceful structure is tolerable.
# Note: if a URL is already in visited links, it shall not appear in START_URLS.

# Spider will generate a result file: "movie.json"
# at path: "doubanMovie-TextSearchEngine\scrapy_crawler\scrapy_crawler"


MAX_MOVIE_PAGE = 10000000000  # infinity

def giveMeUserAgent():
        while True:
            for x in DoubanSpider.userAgentList:
                header = {'User-Agent': x}
                yield header


class DoubanSpider(Spider):
    START_URLS = [
        "http://movie.douban.com/",
        "http://movie.douban.com/top250",
        "http://movie.douban.com/top250?start=25&filter=&type=",
        "http://movie.douban.com/top250?start=50&filter=&type=",
        "http://movie.douban.com/top250?start=75&filter=&type=",
        "http://movie.douban.com/top250?start=100&filter=&type=",
        "http://movie.douban.com/top250?start=125&filter=&type=",
        "http://movie.douban.com/top250?start=150&filter=&type=",
        "http://movie.douban.com/top250?start=175&filter=&type=",
        "http://movie.douban.com/top250?start=200&filter=&type=",
        "http://movie.douban.com/top250?start=225&filter=&type="
    ]
    LAST_SCRAPY_VISITED_LINKS = {}
    LOAD_VISITED_LINKS = False

    name = 'douban'
    allowed_domains = ['douban.com']  # always remember it is a list!!!!
    userAgentList = [
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT6.1; Trident/5.0)',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E) ',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)" '
        ]

    headers = giveMeUserAgent()
    page_count = 0

    def start_requests(self):
        for url in self.START_URLS:
            yield scrapy.http.Request(url, callback=self.parse, headers=self.headers.next())

    def find_last_scrapy_visited_links(self):
        self.LOAD_VISITED_LINKS = True
        try:
            for number in ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh"]:
                with open("visited_links"+number+".json") as f:
                    last_scrapy_visited_links = json.load(f)
                    # print last_scrapy_visited_links
                    # inputs = raw_input()
                    self.LAST_SCRAPY_VISITED_LINKS.update(last_scrapy_visited_links)
        except IOError:
            print "doesn't have visited_links"+number+".json"
            return

    # this function deletes useless strings
    def normalizeArray(self, array):
        newList = []
        for x in array:
            x = x.strip()
            if len(x) > 0:
                newList.append(x)
        return newList

    def createNameList(self, array):
        if len(array) == 0:
            return []
        array = array[0]
        nameList = []
        # array=<a href="/celebrity/1324043/">董成鹏</a> / <a href="/celebrity/1350206/">苏彪</a>
        pattern = re.compile(r"<a href=.*?>(.*?)</a>")
        # print isinstance(array, unicode) array is unicode
        names = re.findall(pattern, array)
        # print names
        for name in names:
            nameList.append(name)
        # print nameList
        # inputs = raw_input()
        return nameList

    def makeMovieLink(self, url):
        if url.find('/subject/') == -1:
            url = ""
            return url
        pattern = re.compile(r"/(\d+?)/")
        s = re.search(pattern, url)
        s = s.groups()[0]
        url = "http://movie.douban.com/subject/" + s + '/'
        return url

    def parse(self, response):
        #   current status
        # print response.url
        if not self.LOAD_VISITED_LINKS:
            self.find_last_scrapy_visited_links()
        # inputs = raw_input()
        sel = Selector(response)

        # this is a movie showing page
        if response.url.find('/subject/') != -1:
            # extract movie information
            item = MovieItem()
            item['F_movieLink'] = [response.url]
            contents = sel.xpath("//div[@id='content']")

            # there is only one content in showing page
            title = contents.xpath("h1/span[@property]/text()").extract()
            year = contents.xpath("h1/span[@class]/text()").extract()
            item['A_movieTitle'] = self.normalizeArray(title)
            item['B_movieYear'] = self.normalizeArray(year)
            intro = sel.xpath("//*[@id='link-report']/span/text()").extract()
            item['E_movieIntro'] = self.normalizeArray(intro)
            contents = sel.xpath('//*[@id="info"]')
            director = contents.xpath('span[1]/span[@class="attrs"]').extract()
            director = self.createNameList(director)
            writer = contents.xpath('span[2]/span[@class="attrs"]').extract()
            writer = self.createNameList(writer)
            actor = contents.xpath('span[3]/span[@class="attrs"]').extract()
            actor = self.createNameList(actor)
            item['C_movieDirector'] = director
            item['movieWriter'] = writer
            item['movieActor'] = actor
            contents = sel.xpath('//*[@id="info"]/span[@property]/text()').extract()  # three results
            item['movieInfo'] = [x.strip() for x in contents]
            contents = sel.xpath('//strong[@class and @property]/text()').extract()
            item['D_movieRating'] = contents
            contents = sel.xpath('//*[@id="interest_sectl"]').extract()
            pattern = re.compile(r'<span property="v:votes">(.*?)</span>')
            string = "".join(contents)
            reResult = re.search(pattern, string)
            if reResult is None:
                item["movieCommentAmount"] = ["1"]
            else:
                item["movieCommentAmount"] = [reResult.group(1)]
            contents = sel.xpath('//div[@id="info"]').extract()
            pattern = re.compile(ur'<span class="pl">又名:</span>(.*?)<br>')
            string = "".join(contents)
            reResult = re.search(pattern, string)
            if reResult is not None:
                aliasList = reResult.group(1).split('/')
                item["A_movieAlias"] = [x.strip() for x in aliasList]
            else:
                item["A_movieAlias"] = []
            contents = sel.xpath('//div[@class="rating_betterthan"]').extract()
            pattern = re.compile('<a href=.*?>(.*?)</a>')
            string = "".join(contents)
            reResults = re.finditer(pattern, string)
            item["movieBetterThan"] = []
            if reResults is not None:
                for reResult in reResults:
                    Lists = reResult.group(1).split()
                    item["movieBetterThan"] += Lists
            # print item["movieBetterThan"]
            # inputs = raw_input()
            yield item

        # find other movies
        pattern = re.compile(r'"http://.*?"')
        htmlBody = response.body.decode(response.encoding)
        result = re.findall(pattern, htmlBody)
        links = []
        for x in result:
            newURL = self.makeMovieLink(x)
            if newURL != "":
                links.append(newURL)

        if self.page_count < MAX_MOVIE_PAGE:
            self.page_count += 1
            print "currently this is page:", self.page_count
            # if self.page_count % 3000 == 0:
            #         print "time to change IP!"
            #         inputs = raw_input()
            for newURL in links:
                if self.LAST_SCRAPY_VISITED_LINKS.get(newURL) is None:
                    yield scrapy.http.Request(newURL, callback=self.parse, headers=self.headers.next())
