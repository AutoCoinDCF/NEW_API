#!/usr/bin/env python
# -*-coding:utf-8-*-

# net login
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import codecs
import os

driver = webdriver.PhantomJS()
#driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
driver.get('https://gw.ict.ac.cn/srun_portal_pc.php?ac_id=1&')

name = driver.find_element_by_name("username")
name.send_keys('user_key')
password = driver.find_element_by_id('password')
password.send_keys('user_value')
password.send_keys(Keys.RETURN)

time.sleep(1)

file_object = codecs.open("dump.html", "w", "utf-8")
html = driver.page_source
file_object.write(html)

driver.quit()
