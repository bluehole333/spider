# -*- coding: utf-8 -*-
"""
程序员客栈 自动ping
Python3.6

"""
import os
import yaml
import time
import requests
import memcache

from selenium import webdriver
from bs4 import BeautifulSoup
from requests.exceptions import *
from selenium.webdriver.common.proxy import Proxy, ProxyType

LOGIN_URL = 'https://www.proginn.com'
PING_URL = 'https://www.proginn.com/wo/work_todo'


class ProxySpider(object):
    def __init__(self):
        """
        初始化cache
        """
        self.cache_key = "PROXYSPIDERX"
        self.cache = memcache.Client(['127.0.0.1:11211'], debug=True)
        self.hash_cache = True if self.cache.get_stats() else False

    def test_proxy(self, proxy):
        proxies = {
            "http": "http://%(ip)s:%(port)s" % proxy,
        }
        if 'HTTPS' in proxy['proxy_type']:
            proxies.update({
                "https": "https://%(ip)s:%(port)s" % proxy,
            })

        # 请求官网首页测试代理是否有效
        try:
            if requests.get(LOGIN_URL, proxies=proxies, timeout=3).status_code == 200:
                return True
        except (ConnectTimeout, ProxyError, ReadTimeout) as e:
            return False

    def spider_proxy_ip(self):
        print("爬取代理网站...")
        proxy = []
        session = requests.Session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Host': 'www.kxdaili.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        html = session.get("http://www.kxdaili.com/dailiip/1/1.html").text
        soup = BeautifulSoup(html, 'lxml')
        for table_tr in soup.find_all('tr'):
            if not table_tr.find_all('td'): continue
            proxy_item = {
                'ip': table_tr.find_all('td')[0].text,
                'port': table_tr.find_all('td')[1].text,
                'proxy_type': table_tr.find_all('td')[3].text,
            }
            if not self.test_proxy(proxy_item): continue
            proxy.append(proxy_item)

        if self.hash_cache:
            self.cache.set(self.cache_key, proxy, 3600 * 24)

        print("共爬取%s有效代理..." % len(proxy))
        return proxy

    @property
    def proxy(self):
        proxys = self.cache.get(
            self.cache_key) or self.spider_proxy_ip() if self.hash_cache else self.spider_proxy_ip()
        return proxys


class ProginnPing(object):
    def __init__(self, user_name, passwd):
        """
        初始化基本信息
        """
        # 初始化用户名和密码
        self.user_name = user_name
        self.passwd = passwd

    def wait_input(self, ele, text):
        for item in text:
            ele.send_keys(item)
            time.sleep(0.5)

    def get_proxy(self):
        proxy_spider_dict = ProxySpider().proxy[0]
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = "%(ip)s:%(port)s" % proxy_spider_dict
        if 'HTTPS' in proxy_spider_dict.get('proxy_type'):
            proxy.ssl_proxy = "%(ip)s:%(port)s" % proxy_spider_dict

        print("使用代理", proxy_spider_dict)
        return proxy

    def ping(self):
        # 使用docker远程调用
        # option = webdriver.Remote(
        #     command_executor="http://chrome:4444/wd/hub",
        #     desired_capabilities=DesiredCapabilities.CHROME
        # )

        firefox_options = webdriver.FirefoxOptions()
        proxy = self.get_proxy()
        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(desired_capabilities)

        print("开始...")
        # 设置火狐为headless无界面模式
        firefox_options.add_argument("--headless")
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--incognito')
        firefox_options.add_argument('--start-maximized')

        option = webdriver.Firefox(firefox_options=firefox_options, desired_capabilities=desired_capabilities,
                                   timeout=10)
        option.maximize_window()

        print("打开登录页面")
        option.get(LOGIN_URL)
        option.implicitly_wait(3)

        print("打开登录悬浮框")
        # 1. 打开登录悬浮框
        links = option.find_element_by_xpath('//a[@class="item login ajax_login_btn"]')
        links.click()

        # 2. 激活手机号登录窗口
        option.find_element_by_id('J_ChangeWay').click()

        # 3. 输入用户名
        user_name = option.find_element_by_xpath('//input[@placeholder="您的手机号"]')
        print('正在输入账号.....')
        self.wait_input(user_name, self.user_name)
        time.sleep(1)

        # 4. 输入密码
        upass = option.find_element_by_id('password')
        print('正在输入密码....')
        self.wait_input(upass, self.passwd)
        time.sleep(1)

        # 5. 点击登录按钮
        butten = option.find_element_by_id('login_submit')
        time.sleep(1)
        butten.click()

        # 6. 登录成功页面跳转
        print('正在跳转ping页面....')
        option.get(PING_URL)
        # 延迟操作3秒
        option.implicitly_wait(3)

        # 7. 点击ping
        option.find_element_by_xpath('//span[@data-position="bottom right"]').click()
        print("点击ping成功")

        return True


def go():
    file_name = 'pro.yaml'
    error = "请添加pro.yaml文件到当前目录，并添加以下内容到yaml文件中:\nusername: 用户名 \npassword: 登录密码"
    if not os.path.exists(file_name):
        print(error)
        return False

    file = open(file_name, 'r', encoding="utf-8")
    user_info = yaml.load(file.read(), Loader=yaml.SafeLoader)
    file.close()
    if not user_info.get('username') or not user_info.get('password'):
        print(error)
        return False

    ProginnPing(str(user_info['username']), str(user_info['password'])).ping()
    return True


if __name__ == '__main__':
    go()
