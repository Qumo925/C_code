import scrapy

class CourseSpider(scrapy.Spider):
    name = 'course_spider'  # 爬虫名称
    allowed_domains = ['icourse163.org']
    start_urls = ['https://www.icourse163.org/course/WHU-1002332010']

    def parse(self, response):
        # 使用 XPath 提取大段文字内容
        course_description = response.xpath('//*[@id="g-body"]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/span[1]/text()').get()

        # 返回提取的数据
        yield {
            'name': course_description.strip() if course_description else None,
        }