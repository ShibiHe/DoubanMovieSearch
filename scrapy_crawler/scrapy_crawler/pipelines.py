# -*- coding: utf-8 -*-
import json
import codecs
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyCrawlerPipeline(object):
    def __init__(self):
        self.file = codecs.open("movie.json", mode="wb", encoding="utf-8")

    def process_item(self, item, spider):
        # some movies have no writer
        if len(item['movieActor']) == 0:
            item['movieActor'] = item['movieWriter']
            item['movieWriter'] = []

        line = json.dumps(dict(item), ensure_ascii=False, sort_keys=True) + '\n'
        self.file.write(line)
        return item

    def open_spider(self, spider):
        # self.file.write('[')
        pass

    def close_spider(self, spider):
        # self.file.seek(-2, 1)
        # self.file.write(']')
        self.file.close()