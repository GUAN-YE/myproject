# -*- coding: utf-8 -*- 
import scrapy
from ..items import MeiItem 
import json




class jin(scrapy.Spider):
    name='pingmei';
    url='http://www.99lib.net/book/2205/'
    shu=65774
    htmm='.htm'
    start_urls= [url + str(shu) + htmm]
    
    



    def parse(self,response):
        
        
        for line in response.xpath('//div[@id="right"]//div[@id="content"]'):
            item = MeiItem()
    #         # item['title']=line.xpath("/h2/text()").extract()[0]
    #         # item['text']=line.xpath('//div/text()').extract()[0]
            
            item['title']=line.xpath('//h2[@class="h2"]/text()').extract()[0]
            item['text']=line.xpath('string(.)').extract()[0]
            # print(item)
            
            
            yield item 
        if self.shu<65876:
            self.shu +=1


          

    #         # print(title,text)
    #         # print json.dumps(title, indent=4, ensure_ascii=False)
    #         # print json.dumps(text, indent=4, ensure_ascii=False)
    #         page=65775
        yield scrapy.Request(self.url + str(self.shu)+ self.htmm ,callback=self.parse)
    # def xia(self,response):
    #     print('.............................')
        



