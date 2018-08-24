# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 8:47
# @Author  : yeshengbao
# @File    : searchain.py

import time

import demjson
import execjs
import hashlib
import requests
import json
import logging
import pymongo
import datetime
from base.user_agent import get_user_agent
from multiprocessing import Process
from base import BloomFilter


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'xinmoney'
MONGO_COLL = 'searchain'
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
node = execjs.get()         # 查看当前
print(node)


class SearChain(object):

    def __init__(self):

        self.requests = requests.session()

    def md5(self, strs):
        """
        哈希函数
        :param strs: 字符串
        :return:
        """
        strs = strs
        strs = hashlib.md5(strs.encode('utf-8'))
        key = strs.hexdigest()
        return key

    def str_json(self, strs):
        """
        str转json
        :param strs:
        :return:
        """
        try:
            str_dict = json.loads(strs)
        except Exception:
            str_dict =  demjson.decode(strs)
        return str_dict

    def _get_sign(self, cartgory=None):
        """
        获取关键参数x-sgin
        :param cartgory: url部分子路径，       代后期完善js驱动
        :return:
        """
        if cartgory == 'addr':
            pass
        file = 'test.js'
        ctx = node.compile(open(file, encoding='utf-8').read())
        js = 'r("{}")'.format(cartgory)
        params = ctx.eval(js)
        params = params.split(',')
        params[0] = self.md5(params[0])
        params = ','.join(params)
        return params

    def _get_html(self, url, headers):
        """
        发起请求函数
        :param url:
        :param headers:
        :return:
        """
        response = requests.get(url=url, headers=headers, timeout=10, verify=False)
        return response.content

    def get_addr_max_page(self, html):
        """
        获取以交易货币的最大页数
        :param html:
        :return:
        """
        str_dict = self.str_json(html)
        data = str_dict.get('data')
        pagenum = data.get('pageNum')
        max_page = int(pagenum) // 10
        return max_page

    def analysis_addr(self, html):
        """
        解析以交易货币地址及其他信息
        :param html:
        :return:
        """
        str_dict = self.str_json(html)
        values_list = str_dict.get('data').get('values')
        item_list = []
        for values in values_list:
            addr = values.get('addr', '')
            addr_url = 'http://www.searchain.io/address?address=' + addr
            balance = values.get('balance')
            balance_sta_usd_price = values.get('balance_sta_usd_price', '')
            first_in_time = values.get('first_in_time', '')
            first_out_time = values.get('first_out_time', '')
            in_val = values.get('in_val', '')
            last_in_time = values.get('last_in_time', '')
            last_out_time = values.get('last_out_time', '')
            out_val = values.get('out_val', '')
            rank_no = values.get('rank_no', '')
            tag = values.get('tag', '')
            trans_in_cnt = values.get('trans_in_cnt', '')
            trans_out_cnt = values.get('trans_out_cnt', '')
            trans_perc = values.get('trans_perc', '')
            item_list.append(
                {
                    'rank_no': rank_no,
                    'addr': addr,
                    'addr_url': addr_url,
                    'balance': balance,
                    'balance_sta_usd_price': balance_sta_usd_price,
                    'first_in_time': first_in_time,
                    'first_out_time': first_out_time,
                    'in_val': in_val,
                    'last_in_time': last_in_time,
                    'last_out_time': last_out_time,
                    'out_val': out_val,
                    'tag': tag,
                    'trans_in_cnt': trans_in_cnt,
                    'trans_out_cnt': trans_out_cnt,
                    'trans_perc': trans_perc,
                }
            )
        return item_list

    def get_addr_html(self, token_address):
        """
        获取以交易网址
        :param token_address:
        :return:
        """
        url = "http://scvelk.searchain.io/open/currencies/graph?type=get_token_value_list&tokenAddr={}&pageNo=1".format(token_address)
        cartgory = 'pageNo=1&tokenAddr={}&type=get_token_value_list'.format(token_address)
        headers = {'User-Agent': get_user_agent(), 'X-SIGN': self._get_sign(cartgory=cartgory)}
        html = self._get_html(url, headers=headers).decode('utf-8')
        max_page = self.get_addr_max_page(html)
        item_lists = []
        for page in range(1, int(max_page)+1):
            url = "http://scvelk.searchain.io/open/currencies/graph?type=get_token_value_list&tokenAddr={}&pageNo={}".format(token_address, page)
            cartgory = 'pageNo={}&tokenAddr={}&type=get_token_value_list'.format(page, token_address)
            headers = {'User-Agent': get_user_agent(), 'X-SIGN': self._get_sign(cartgory=cartgory)}
            html = self._get_html(url, headers=headers).decode('utf-8')
            addr_info = self.analysis_addr(html)
            item_lists.append(addr_info)
        return item_lists

    def analysis_list_info(self, html):
        """
        解析列表页信息及子信息
        :param html:
        :return:
        """
        data_list = html.get('data').get('lists')
        if data_list:
            for data in data_list:
                try:
                    token_address = data.get('token_address')
                    rank = data.get('rank', '')
                    coin_type = data.get('coin_type', '')
                    publish_date = data.get('publish_date', '')
                    publish_cnt_flow_cnt = str(data.get('publish_cnt', '')) + '/' + str(data.get('flow_cnt', ''))
                    pre_trans_cnt = data.get('pre_trans_cnt', '')
                    addr_content = self.get_addr_html(token_address)
                    yield {
                        'rank': rank,
                        'coin_type': coin_type,
                        'publish_date': publish_date,
                        'publish_cnt_flow_cnt': publish_cnt_flow_cnt,
                        'pre_trans_cnt': pre_trans_cnt,
                        'addr_content': addr_content,
                    }
                except:
                    pass


    def save_mongo(self, content):
        """
        入库mongo
        :param content:
        :return:
        """
        client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        db = client[MONGO_DB]
        coll = db[MONGO_COLL]
        coll.update(dict(content), {'$set': {'title': dict(content)['coin_type']}}, True)
        print('数据添加成功： ' + str(content))

    def begin_spider(self, page):
        """
        入口函数
        :param page: 最大页数
        :return:
        """
        url='http://scvelk.searchain.io/open/currencies/get_hot_token?orderBy=pre_trans_cnt&size=50&page={}&type=info&token='.format(page)
        cartgory = 'orderBy=pre_trans_cnt&page={}&size=50&token=&type=info'.format(page)
        headers = {'User-Agent': get_user_agent(), 'X-SIGN': self._get_sign(cartgory=cartgory)}
        while True:
            html = self._get_html(url, headers=headers).decode('utf-8')
            html = self.str_json(html)
            if html.get('errno') == 200:
                break
        content = self.analysis_list_info(html)
        for con in content:
            self.save_mongo(con)


if __name__ == '__main__':

    start_time = datetime.datetime.now()  # 程序开始时间
    searchain = SearChain()
    process_lists = []
    # 启动进程池
    for page in range(1, 16):
        while True:
            if len(process_lists) < 8:
                th = Process(target=searchain.begin_spider, args=(page,))
                th.start()
                process_lists.append(th)
                break
            else:
                time.sleep(3)
                print(process_lists)
                print('进程池已经满了')
                for ths in process_lists:
                    if not ths.is_alive():
                        process_lists.remove(ths)
    for ths in process_lists:
        ths.join()

    over_time = datetime.datetime.now()  # 程序结束时间
    total_time = (over_time - start_time).total_seconds()
    print('程序共计%s秒' % total_time)
