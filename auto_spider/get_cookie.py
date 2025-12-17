from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time

browser_options = Options()
browser = webdriver.Chrome(options=browser_options)
print("浏览器已成功创建。")


def get_cookie(url='https://weibo.com/login.php'):
    browser.get(url)
    print('请在25秒内，使用微博APP扫码登录你的账号...')
    time.sleep(25)
    with open('cookies.txt', 'w') as f:
        f.write(json.dumps(browser.get_cookies()))
        f.close()
    print('已成功保存cookie信息。')


if __name__ == '__main__':
    get_cookie()
