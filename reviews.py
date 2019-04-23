# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import os


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['amazon.in']
    start_urls = ['https://www.amazon.in/Smartphones/b?ie=UTF8&node=1805560031']

    def parse(self, response):
        phones_container = response.xpath('//ul[contains(@class,"s-result-list")]')
        phones = phones_container.xpath('.//li[contains(@id,"result")]')
        for phone in phones:
            phone_absolute_url = phone.css('a[class*=s-access]::attr(href)').get()
            yield Request(phone_absolute_url,callback=self.parse_phone_details)
            #print(phone.css('a[class*=s-access]::attr(href)').get())
    
    def parse_phone_details(self, response):
        phone_name = response.xpath('//span[contains(@id,"productTitle")]/text()').extract_first().strip()
        product_details = response.xpath('//div[contains(@id,"prodDetails")]')
        technial_details = product_details.xpath('.//div[contains(@class,"pdTab")]')[0]
        feature_names = technial_details.xpath('.//td[contains(@class,"label")]/text()').extract()
        feature_values = technial_details.xpath('.//td[contains(@class,"value")]/text()').extract()
        features_data = dict(zip(feature_names,feature_values))
        print (features_data)

        additional_info = product_details.xpath('.//div[contains(@class,"pdTab")]')[1]
        is_user_reviews_exist = not additional_info.xpath('.//tr[contains(@class,"customer_reviews")]')\
                                .xpath('.//a/text()')\
                                .extract_first().strip() == "Be the first to review this item"
        if(is_user_reviews_exist):
            reviews_url = additional_info.xpath('.//tr[contains(@class,"customer_reviews")]')\
                .xpath('.//a[contains(@class,"link")]/@href')\
                .extract_first()
            yield  Request(reviews_url,callback=self.parse_phone_reviews,meta={'phone_name':phone_name})
        #yield features_data
    
    def parse_phone_reviews(self,response):
        phone_name = response.meta['phone_name']
        reviews = response.xpath('//div[contains(@id,"customer_review")]')
        if os.path.exists(phone_name+'.txt'):
            append_write = 'a'
        else:
            append_write = 'w'

        with open(phone_name +'.txt',append_write) as fp:
            for review in reviews:
                review_text = ' '.join(review.xpath('.//span[contains(@data-hook,"review-body")]/text()').extract())
                for line in review_text:
                    fp.write(line)
                fp.write('\n')
        next_page_url = response.xpath('//li[contains(@class,"a-last")]/a/@href').extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)
        yield Request(absolute_next_page_url,callback=self.parse_phone_reviews,meta={'phone_name':phone_name})

        
