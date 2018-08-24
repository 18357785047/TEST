# -*- coding: utf-8 -*-
# @Time    : 2018/8/20 16:26
# @Author  : yeshengbao
# @File    : two.py
import time

import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



class SearChain(object):
    def __init__(self):
        self.webdir = webdriver.Chrome()
        self.url = 'http://www.searchain.io/alltokenlist'


    def _get_html(self, url, headers):
        response = requests.get(url=url, headers=headers, timeout=10, verify=False)
        return response.content

    def analysis_max_page(self, html):
        doc = etree.HTML(html)
        try:
            max_page = doc.xpath('.//ul[contains(@class, "text_right")]/li[last()-1]/a/text()')
            return max_page[0]
        except:
            return 1

    def get_max_page(self):
        """
        获取最大页数
        :return: 最大页码
        """
        self.webdir.get('http://www.searchain.io/alltokenlist')
        self.webdir.maximize_window()
        try:
            WebDriverWait(self.webdir, 15).until(EC.presence_of_element_located((By.XPATH, './/ul[contains(@class, "text_right")]/li[last()-1]')))
        except:
            print('正在等待最大页码！！！')
            self.get_max_page()
        html = self.webdir.page_source
        max_page = self.analysis_max_page(html)
        return max_page

    def analysis_token_list(self):
        doc = etree.HTML(self.webdir.page_source)
        tr_list = doc.xpath('.//tbody[@class="ivu-table-tbody"]/tr[@class="ivu-table-row"]')
        for index,tr in enumerate(tr_list):
            if index >= 50:
                break
            token_sort = ''.join(tr.xpath('./td[1]/div[@class="ivu-table-cell"]/div/p/text()')).replace('Top', '')
            token_name = ''.join(tr.xpath('./td[2]/div[@class="ivu-table-cell"]/div/div/text()'))
            token_circulation_circulation = ''.join(tr.xpath('./td[3]/div[@class="ivu-table-cell"]/div/p/text()'))
            token_transaction_number = ''.join(tr.xpath('./td[4]/div[@class="ivu-table-cell"]/div/text()'))
            print(token_sort, token_name)
            # yield {
            #     'token_sort': token_sort,
            #     'token_name': token_name,
            #     'token_circulation_circulation': token_circulation_circulation,
            #     'token_transaction_number': token_transaction_number,
            # }


    def get_all_page(self, page):
        """
        对每一个的token进行获取与请求
        :param page: 当前页数
        :return:
        """
        next = WebDriverWait(self.webdir, 15).until(EC.presence_of_element_located(
            (By.XPATH, './/div[@class="ivu-page-options-elevator"]/input[@type="text"]')))
        next.clear()
        next.send_keys(page)
        next.send_keys(Keys.ENTER)
        token_list_content = self.analysis_token_list()

        for i in range(1, 51):  # 每一页的最大条数
            try:
                WebDriverWait(self.webdir, 15).until(EC.presence_of_element_located((By.XPATH, './/tbody[@class="ivu-table-tbody"]/tr[{}]'.format(i)))).click()
                handles = self.webdir.window_handles  # 获取当前全部窗口句柄集合
                self.webdir.switch_to.window(handles[1])  # 切换到第二个窗口
                self.webdir.close()  # 关闭第二个窗口
                self.webdir.switch_to.window(handles[0])  # 切换到第一个窗口
            except:
                print('没有此页面')
                pass

    def begin_spider(self):
        max_page = self.get_max_page()
        for page in range(1, int(max_page)+1):
            self.get_all_page(page)



searchain = SearChain()
searchain.begin_spider()


#################################