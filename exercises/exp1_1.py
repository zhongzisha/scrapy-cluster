import re
import parsel
from urllib import request
import asyncio  # 异步操作
from datetime import datetime
from lxml import etree
from time import time
import aiohttp

def exp1():
    url = "https://www.phei.com.cn/gywm/cbsjj/2010-11-19/47.shtml"
    with request.urlopen(url) as req:
        text = req.read().decode('utf-8')
        title = re.search("<h1>(.*)</h1>", text).group(1)
        sel = parsel.Selector(text)
        content = "\n".join(sel.css(".column_content_inner p font::text").extract())
        with open("about.txt", "a") as fp:
            fp.write(title)
            fp.write("\n")
            fp.write(content)


'''
也可以将urlopen方法换成get方法，例如
req = requests.get(url)
text = req.content.decode('utf-8')
'''

'''
post方法
head = {'User-Agent': 'Mozilla/5.0'}
info = {'username':'abc', 'password':'abc'}
response = requests.post(url, data=info, headers=head, timeout=0.8) # 0.8秒未收到响应则引发异常
'''

'''
协程被引入python之后，支持async, await等关键字。协程主要用于IO密集应用中。
'''


async def wait():
    asyncio.sleep(5)
    print('等待5秒')


async def print_time(word):
    print(word, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


async def main1():
    await print_time('begin')
    await wait()
    await print_time('end')


async def main2():
    await print_time('begin')
    await wait()
    await wait()
    await wait()
    await wait()
    await wait()
    await print_time('end')


def run1():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main1())
    loop.close()


def run2():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main2())
    loop.close()


async def run3():
    print('begin', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    await asyncio.sleep(5)
    print('end', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == '__main__':
    # run1()
    # run2()
    asyncio.run(run3())