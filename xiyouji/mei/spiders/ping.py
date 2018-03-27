# -*- coding: utf-8 -*- 
import scrapy
from ..items import MeiItem 
import json




class jin(scrapy.Spider):
    
    name='xiyouji';
    url='http://www.booktxt.net/2_2225/'
    shu=760809
    htmm='.html'
    start_urls= [url + str(shu) + htmm]
    
    



    def parse(self,response):
        
        
        for line in response.xpath('//div[@id="wrapper"]//div[@class="content_read"]//div[@class="box_con"]'):
            item = MeiItem()
    #         # item['title']=line.xpath("/h2/text()").extract()[0]
    #         # item['text']=line.xpath('//div/text()').extract()[0]
            
            # item['title']=line.xpath('//h2[@class="h2"]/text()').extract()[0]
            item['title']=line.xpath('//div[@class="bookname"]/h1/text()').extract()[0]
            for line in response.xpath('//div[@id="content"]'):
                item['text']=line.xpath('string(.)').extract()[0]
            # print(item)
            
            
            yield item 
        if self.shu<=3145103:
            self.shu +=1


          

    #         # print(title,text)
    #         # print json.dumps(title, indent=4, ensure_ascii=False)
    #         # print json.dumps(text, indent=4, ensure_ascii=False)
    #         page=65775
        yield scrapy.Request(self.url + str(self.shu)+ self.htmm ,callback=self.parse)
    # def xia(self,response):
    #     print('.............................')
        



