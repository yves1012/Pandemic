# -*- coding: utf-8 -*-

"""
@desc: 抓取所有 Shopify 网站
@file: crawl_shopify.py
@author: Yves Yu
@contact: service@yvesyu.com
@time: 2023/2/14 20:26
"""

import re
import pandas as pd
import requests
from multiprocessing import Pool

HEADERS = {
    'user-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}
PROXIES = {'https': '127.0.0.1:7890'}


def parse_site():
    """
    解析域名文档
    :return: 返回域名列表
    """
    with open('./crawl_shopify.txt', 'r', encoding='utf-8') as f:
        site_data = f.readlines()
        return ["https://" + site.strip('\n') for site in site_data]


def parse_title(text):
    """
    解析网页标题
    :param text: 网站源码
    :return: 网页标题
    """
    if len(text) > 0:
        title = re.findall(r'<title>(.*?)</title>', text)
        if len(title) == 0:
            title = re.findall(r'<meta property="og:title" content="(.*?)">', text)
            if len(title) == 0:
                title = ["No Title"]
    # 过滤脏字符
    return title[0].replace("&#39;", "'").replace("&amp;", "&")


def parse_desc(text):
    """
    解析网页描述
    :param text: 网站源码
    :return: 网页描述
    """
    if len(text) > 0:
        desc = re.findall(r'<meta property="og:description" content="(.*?)">', text)
        if len(desc) == 0:
            desc = re.findall(r'<meta name="description" content="(.*?)">', text)
            if len(desc) == 0:
                desc = re.findall(r'<meta content="(.*?)" name="description">', text)
                if len(desc) == 0:
                    desc = ["No Desc"]
    return desc[0].replace("&#39;", "'").replace("&amp;", "&")


def crawl_site_info(url):
    """
    抓取网站的基础信息
    :param url: 链接
    :return: 网站信息数组
    """
    try:
        # 抓取网页信息
        res = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=30)
        if res.status_code == 200:
            print("网站 %s 信息抓取成功" % url)
            return [url, parse_title(res.text), parse_desc(res.text)]
    except requests.exceptions.ConnectionError:
        print("%s crawl error" % url)


if __name__ == '__main__':
    pool = Pool(processes=10)
    pool_res = pool.map(crawl_site_info, parse_site())
    # 导出 CSV 文件
    columns = ["URL", "Title", "Desc"]
    site_pd = pd.DataFrame(list(filter(None, pool_res)))
    site_pd.to_csv("/Users/yves/Desktop/shopify.csv", mode='a', header=columns, index=False, encoding="utf-8")
    pool.terminate()
