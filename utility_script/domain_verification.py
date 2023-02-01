# -*- coding: utf-8 -*-

"""
@desc: 根据品牌商标信息，验证品牌商标 .com 域名是否注册
@file: domain_verification.py
@author: Yves Yu
@contact: service@yvesyu.com
@time: 2023/2/1 14:51
"""

import requests
import json
import xmltodict
import time


def domain_verify(brand_domain):
    """
    验证品牌域名是否注册
    :param brand_domain: 品牌域名
    :return: 注册与否信息
    """
    url = "http://panda.www.net.cn/cgi-bin/check.cgi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us",
        "Connection": "keep-alive",
        "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
    }
    # 发送查询请求并解码查询结果
    search_res = requests.post(url, {"area_domain": brand_domain}, headers=headers, allow_redirects=False)
    parse_res = search_res.content.decode("utf-8")
    # 将查询结果从 XML 格式转换为 JSON 格式
    try:
        json_res = json.loads(json.dumps(xmltodict.parse(parse_res, encoding="utf-8")))
    except Exception:
        json_res = {
            "property": dict(returncode=-1, key=brand_domain, original="000")
        }
    return json_res["property"]


if __name__ == '__main__':
    # 打开品牌信息文档
    with open('./domain_brand.txt', 'r') as f:
        brand_list = list(set(f.readlines()))
    # 循环处理品牌信息
    for brand in brand_list:
        domain = brand.strip('\n') + '.com'
        try:
            domain_res = domain_verify(domain)
            # 异常状态则重新抓取
            if domain_res['original'] == '000':
                i = 1
                while i < 4:
                    i = i + 1
                    time.sleep(1)
                    domain_res = domain_verify(domain)
                    if domain_res['original'] != '000':
                        break
            # 打印出可注册的域名
            if domain_res['original'] != "211 : Domain exists":
                print(domain_res)
        except Exception as e:
            print("异常品牌是：{}".format(brand))
        time.sleep(1)
