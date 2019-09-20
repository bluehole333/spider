# -*- coding: utf-8 -*-
"""
程序员客栈 自动ping
Python3

"""

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time

LOGIN_URL = 'https://www.proginn.com/'
PING_URL = 'https://www.proginn.com/wo/work_todo'

# 登录用户名和密码
USER_NMAE = ''
PASSWD = ''


class ProginnPing(object):
    def __init__(self, headers, user_name, passwd):
        """
        类的初始化
        """
        self.headers = headers
        # 初始化用户名和密码
        self.user_name = user_name
        self.passwd = passwd

    def wait_input(self, ele, text):
        for item in text:
            ele.send_keys(item)
            time.sleep(0.5)

    def ping(self):
        option = webdriver.Firefox()
        option.maximize_window()
        option.get(LOGIN_URL)
        option.implicitly_wait(3)

        # 1. 打开登录悬浮框
        links = option.find_element_by_xpath('//a[@class="item login ajax_login_btn"]')
        links.click()

        # 2. 激活手机号登录窗口
        option.find_element_by_id('J_ChangeWay').click()

        # 3. 输入用户名
        uname = option.find_element_by_xpath('//input[@placeholder="您的手机号"]')
        print('正在输入账号.....')
        self.wait_input(uname, self.user_name)
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

        print('正在跳转页面....')
        option.get(PING_URL)
        print('当前页面:', option.current_url)
        option.implicitly_wait(3)

        # 8. ping
        option.find_element_by_xpath('//span[@data-position="bottom right"]').click()

        return True


# 自定义headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Referer': 'https://www.proginn.com/wo/work_todo',
    'Host': 'www.proginn.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive'
}

if __name__ == '__main__':
    ProginnPing(HEADERS, USER_NMAE, PASSWD).ping()
