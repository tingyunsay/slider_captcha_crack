#!/usr/bin/env python
# !coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import sys, os
import re, logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.common import exceptions
from selenium.webdriver.common.proxy import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import random

#author -- tingyun
#done 2018-03-02

dcap = dict(DesiredCapabilities.PHANTOMJS)
#pc端的ua
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Ch"
    "rome/62.0.3202.94 Safari/537.36"
        )

#模拟登录淘宝类
class Taobao:
    #初始化方法
    def __init__(self):
        #阿里妈妈登录的url
        #self.loginURL = "https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&css_style=alimama&from=alimama&redirectURL=http%3A%2F%2Fwww.alimama.com&full_redirect=true&disableQuickLogin=true"

        #淘宝登录的url
        self.loginURL = "https://login.taobao.com/member/login.jhtml"

        #模拟早期淘宝简单拖动验证的url
        #self.loginURL = "http://hanekaoru.com/demo/js/%E6%B7%98%E5%AE%9D%E7%99%BB%E5%BD%95/index.html"

        self.TPL_username = ''
        self.TPL_password = ''

        #self.driver = webdriver.PhantomJS(executable_path = "/home/node/node_modules/phantomjs-prebuilt/bin/phantomjs")
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        #登录POST数据时发送的头部信息
        self.loginHeaders =  {
            'Host':'login.taobao.com',
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Referer' : 'https://login.taobao.com/member/login.jhtml',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive'
        }
    #登录获取cookie
    def login(self):
        self.driver.delete_all_cookies()
        self.driver.set_page_load_timeout(15)
        self.driver.get(self.loginURL)
        #等待3秒使得页面完全渲染出来
        time.sleep(3)
        self.switchFromLogin()
        self.inputUserName()
        #self.driver.save_screenshot("username.png")
        time.sleep(1)

        flags = True
        while flags:
            self.inputPassword()
            slide_div = self.driver.find_element_by_id("nocaptcha")
            if slide_div.is_displayed() is True:
                retry = 0
                while retry < 5:
                    retry += 1
                    slide_span = self.driver.find_element_by_xpath("//*[@id='nc_1_n1z']")  # 取得滑块span
                    ActionChains(self.driver).click_and_hold(slide_span).perform()  # 鼠标左键按住span

                    slide_y = slide_span.location['y']
                    print "slide_y:"+str(slide_y)
                    """
                    '''
                    1.这里是网上的一个版本，模拟的轨迹计算图，但在这里貌似效果不太好
                    '''
                    result = path1(300)
                    for x in result:
                        ActionChains(self.driver).move_by_offset(xoffset=x[0], yoffset=x[1]).perform()
                        time.sleep(x[-1])
                        #ActionChains(self.driver).move_to_element_with_offset(to_element=slide_span, xoffset=x[0],yoffset=x[1]).perform()
                    """

                    '''
                    2.当前的版本，需要改进这个生成轨迹图的方法
                    '''
                    track_list = get_track(258)     #这个get_track()是原作者破解极验的一个轨迹图生成算法，极验能通过，但淘宝无法通过。考虑到淘宝可能是机器学习的辨别
                    track_string = ""
                    #这边滑块的高度为：42，宽度为：40
                    for track in track_list:
                        track_string = track_string + "{%d,%d}," % (track, 19)
                        ActionChains(self.driver).move_to_element_with_offset(to_element=slide_span, xoffset=track + 21,yoffset=19).perform()
                        time.sleep(random.randint(10, 50) / 100)
                    print track_string

                    """
                    '''
                    3.平行移动的版本
                    '''
                    for index in range(20):
                        try:
                            ActionChains(self.driver).move_by_offset(20, 0).perform()  # 平行移动鼠标
                        except Exception as e:
                            print(e)
                            break
                        if (index == 19):
                            ActionChains(self.driver).release(slide_span).perform()
                            time.sleep(1)
                        else:
                            time.sleep(0.01)  # 等待停顿时间
                            time.sleep(0.1)
                    time.sleep(110)
                    """

                    ActionChains(self.driver).release(slide_span).perform()
                    text = self.driver.find_element_by_xpath("//div[@id='nc_1__scale_text']/span")
                    print text.text
                    try:
                        slide_refresh = self.driver.find_element_by_xpath(
                            "//div[@id='nocaptcha']/div/span/a")  # 页面没有滑块，而是“点击刷新再来一次”
                        slide_refresh.click()
                    except exceptions.NoSuchElementException:  # 滑动成功
                        break
            time.sleep(2)
            self.driver.find_element_by_id("J_SubmitStatic").click()
            time.sleep(3)
            if self.driver.find_element_by_id("nocaptcha").is_displayed() is True:
                print "出现了滑块，日尼玛，重新跑一遍"
            else:
                flags = False

        self.driver.save_screenshot("ojbk.png")
        time.sleep(2)
        self.driver.close()

    #切换普通表单登陆
    def switchFromLogin(self):
        self.driver.find_element_by_id("J_Quick2Static").click()

    def inputUserName(self):
        user_name = self.driver.find_element_by_id("TPL_username_1")
        user_name.clear()
        #添加抖动，使得出现滑块的概率减小，基本上登录就能成功
        ActionChains(self.driver).move_by_offset(random.randint(10,60), random.randint(10,60)).perform()
        for i in self.TPL_username:
            user_name.send_keys(i)
            time.sleep(0.2)

    def inputPassword(self):
        password = self.driver.find_element_by_id("TPL_password_1")
        password.clear()
        #添加抖动，使得出现滑块的概率减小，基本上登录就能成功
        ActionChains(self.driver).move_by_offset(random.randint(10,60), random.randint(10,60)).perform()
        for i in self.TPL_password:
            password.send_keys(i)
            time.sleep(0.2)

    def main(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.login()

#重写这个轨迹生成图，应该是先快后慢
def get_track(length):
    '''
    根据缺口的位置模拟x轴移动的轨迹
    '''
    pass
    list=[]
#     间隔通过随机范围函数来获得
    x=random.randint(1,3)
    while length-x>=5:
        list.append(x)
        length=length-x
        x=random.randint(3,8)
    for i in xrange(length):
        list.append(1)
    return list

def path1(distance):
    """绘制移动路径方法1，构造一个等比数列"""
    q = 0.4  # 测试后发现0.4效果最佳
    n = 10  # 最多移动几次
    a1 = ((1 - q) * distance) / (1 - q ** n)
    result = []
    for o in range(1, n + 1):
        an = a1 * q ** (o - 1)
        if an < 0.1:  # 小于移动阈值的就不要了
            break
        t = random.uniform(0, 0.5)  # 测试后0.5秒的间隔成功率最高
        result.append([an, 0, t])
    return result

def path2(distance):
    """绘制移动路径方法2,模拟物理加速、减速运动，效果比1好"""
    result = []
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 0
    while current < (distance - 10):
        if current < mid:
            # 加速度为正2
            a = 2
        else:
            # 加速度为负3
            a = -3
        # 初速度v0
        v0 = v
        # 当前速度v = v0 + at
        v = v0 + a * t
        # 移动距离x = v0t + 1/2 * a * t^2
        move = v0 * t + 0.5 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        result.append([round(move), 0, random.uniform(0, 0.5)])
    return result


if __name__ == '__main__':
    taobao = Taobao()
    taobao.main()
