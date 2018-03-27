# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import os
import json



class MeiPipeline(object):
    def process_item(self, item, spider):
        
        with open('E:/shu.txt','a',encoding='utf8') as f:
            # line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            f.write(item['title'] + '\n')
            f.write(str(item['text']) + '\n')
            # f.write(item)

        
        return item
