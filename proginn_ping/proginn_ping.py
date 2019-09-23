# -*- coding: utf-8 -*-
"""
程序员客栈 自动ping
Python3.6

"""
import os
import yaml
import time

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

LOGIN_URL = 'https://www.proginn.com'
PING_URL = 'https://www.proginn.com/wo/work_todo'


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

    def ping(self):
        print("开始....")

        # 使用docker远程调用
        # option = webdriver.Remote(
        #     command_executor="http://chrome:4444/wd/hub",
        #     desired_capabilities=DesiredCapabilities.CHROME
        # )

        firefox_options = webdriver.FirefoxOptions()

        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = "47.110.130.152:8080"
        # prox.socks_proxy = "47.110.130.152:8080"
        proxy.ssl_proxy = "47.110.130.152:8080"
        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(desired_capabilities)

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
