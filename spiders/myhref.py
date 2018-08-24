# -*- coding: utf-8 -*-
# @Time    : 2018/8/21 17:21
# @Author  : yeshengbao
# @File    : myhref.py


import requests
import json
from lxml import etree
import re
import time
import logging
from base.user_agent import get_user_agent
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MyhrefCoding(object):
    def __init__(self, url='http://v.myhref.com/api/v2/git/datas?callback=jQuery111304036066670464642_1534843443097&sortBy=addCodesCountAWeek&_=1534843443098'):
        self.headers = {
            'User-Agent': get_user_agent(),

            }
        self.url = url
        self.requests = requests.session()

    def _get_html(self, url, headers):
        """
        请求html
        :param url:
        :param headers:
        :return:
        """
        while True:
            response = self.requests.get(url=url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.content

    def str_date(self, str):
        """
        时间戳转日期
        :param str:
        :return:
        """
        timeStamp = str
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def analysis_moneycoding(self, html):
        """
        解析列表页信息
        :param html:
        :return:
        """
        strs = re.findall('jQuery\d+_\d+\((.*?)\)', html, re.S)
        if strs:
            strs = strs[0]
            str_dic = json.loads(strs)
            list_infos = str_dic.get('infos')
            for infos in list_infos:

                # 代码
                code = infos.get('code', '')

                name = infos.get('name', '')

                # git子域
                owner = infos.get('owner', '')

                # 项目库
                repo = infos.get('repo', '')

                # 创建时间
                createTime = int(str(infos.get('createTime', ''))[:-3])
                createTime = self.str_date(createTime)

                # 更新时间
                updateTime = int(str(infos.get('updateTime', ''))[:-3])
                updateTime = self.str_date(updateTime)

                pushTime = int(str(infos.get('pushTime', ''))[:-3])
                pushTime = self.str_date(pushTime)

                size = infos.get('size', '')

                # 关注数
                watchersCount = infos.get('watchersCount', '')

                # 问题数
                openIssuesCount = infos.get('openIssuesCount', '')

                # 订阅数
                subscribersCount = infos.get('subscribersCount', '')

                # 编程语言
                language = infos.get('language', '')

                # 分支数
                forksCount = infos.get('forksCount', '')

                # 代码量（本周）
                addCodesCountAWeek = infos.get('addCodesCountAWeek', '')

                delCodesCountAWeek = infos.get('delCodesCountAWeek', '')

                # 提交次数（本周）
                commitCountAWeek = infos.get('commitCountAWeek', '')

                # 代码量（近一个月）
                addCodesCountAMonth = infos.get('addCodesCountAMonth', '')

                delCodesCountAMonth = infos.get('delCodesCountAMonth', '')

                # 提交次数（近一个月）
                commitCountAMonth = infos.get('commitCountAMonth', '')

                # 代码量（上周）
                addCodesCountLastWeek = infos.get('addCodesCountLastWeek', '')

                delCodesCountLastWeek = infos.get('delCodesCountLastWeek', '')

                # 提交次数（上周）
                commitCountLastWeek = infos.get('commitCountLastWeek', '')

                trading = infos.get('trading', '')

                yield {
                    'code': code,
                    'name': name,
                    'owner': owner,
                    'repo': repo,
                    'createTime': createTime,
                    'updateTime': updateTime,
                    'pushTime': pushTime,
                    'size': size,
                    'watchersCount': watchersCount,
                    'openIssuesCount': openIssuesCount,
                    'subscribersCount': subscribersCount,
                    'language': language,
                    'forksCount': forksCount,
                    'addCodesCountAWeek': addCodesCountAWeek,
                    'delCodesCountAWeek': delCodesCountAWeek,
                    'commitCountAWeek': commitCountAWeek,
                    'addCodesCountAMonth': addCodesCountAMonth,
                    'delCodesCountAMonth': delCodesCountAMonth,
                    'commitCountAMonth': commitCountAMonth,
                    'addCodesCountLastWeek': addCodesCountLastWeek,
                    'delCodesCountLastWeek': delCodesCountLastWeek,
                    'commitCountLastWeek': commitCountLastWeek,
                    'trading': trading,
                }

    def get_max_page(self, html):
        """
        获取列表页最大页数
        :param html:
        :return:
        """
        try:
            doc = etree.HTML(html)
            max_page = doc.xpath('.//div[@class="pagination"]/em[@class="current"]/@data-total-pages')
            if max_page:
                max_page = max_page[0]
            else:
                max_page = 1
            return max_page
        except:
            return 1

    def analysis_git_list(self, html, item_list):
        """
        解析git列表页信息
        :param html:
        :param item_list:
        :return:
        """

        doc = etree.HTML(html)
        li_list = doc.xpath('.//div[contains(@class, "repo-list")]/li | .//div[contains(@class, "org-repos")]/li')
        for li in li_list:
            item = {}
            git_library_name = ''.join(li.xpath('./div[contains(@class, "d-inline-block")]/h3/a/text()')).replace('\n', '').replace(' ','')
            git_library_url = 'https://github.com' + ''.join(li.xpath('./div[contains(@class, "d-inline-block")]/h3/a/@href'))
            git_desc = ''.join(li.xpath('./div[2]//text()')).replace('\n', '').replace(' ', '')
            try:
                git_language = ''.join(li.xpath('./div[contains(@class, "text-gray")]/span[@class="mr-3"]/text()')).replace('\n', '').replace(' ','')
            except:
                git_language = ''
            try:
                git_star = ''.join(li.xpath('./div[contains(@class, "mt-2")]/a[1]/text()')).replace('\n', '').replace(' ','')
            except:
                git_star = 0

            try:
                git_fork = ''.join(li.xpath('./div[contains(@class, "text-gray")]/a[2]/text()')).replace('\n', '').replace(' ','')
            except:
                git_fork = 0
            update_time = 'update: ' + ''.join(li.xpath('./div[contains(@class, "text-gray")]/relative-time/text()'))
            is_issue = ''.join(li.xpath('./div[contains(@class, "text-gray")]/a[3]/@href')).replace('\n', '').replace(' ','')
            if is_issue:
                is_issue = 'https://github.com' + ''.join(li.xpath('./div[contains(@class, "text-gray")]/a[3]/@href')).replace('\n', '').replace(' ','')
            else:
                pass
            item['git_library_name'] = git_library_name
            item['git_library_url'] = git_library_url
            item['git_desc'] = git_desc
            item['git_language'] = git_language
            item['git_star'] = git_star
            item['git_fork'] = git_fork
            item['update_time'] = update_time
            item['is_issue'] = is_issue
            item_list.append(item)

    def handle_git(self, git_url):
        """
        分析git列表页
        :param git_url:
        :return:
        """

        html = self._get_html(git_url, headers=self.headers).decode('utf-8')
        max_page = self.get_max_page(html)
        item_list = []
        for page in range(1, int(max_page)+1):
            git_urls = git_url + '?page={}'.format(page)
            html = self._get_html(git_urls, headers=self.headers).decode('utf-8')
            cont = self.analysis_git_list(html, item_list)
        return item_list

    def save_mysql(self, items):
        pass

    def begin_spider(self):
        """

        :return:
        """
        html = self._get_html(self.url, headers=self.headers).decode('utf-8')
        doc = self.analysis_moneycoding(html)
        for i in doc:
            print(i)
            git_url = 'https://github.com/' + i.get('owner')
            git_doc = self.handle_git(git_url)
            items = dict(i, **{'git': git_doc})
            log.info(items)
            self.save_mysql(items)


if __name__ == '__main__':
    myhrefcoding = MyhrefCoding()
    myhrefcoding.begin_spider()
