# import re
# import parsel
# from urllib import request
# import asyncio  # 异步操作
# from datetime import datetime
# from lxml import etree
# from time import time
# import aiohttp
# import random
#
# url = "https://movie.douban.com/top250"
#
# header = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
#     "content-type": "text/plain;charset=UTF-8",
# }
#
#
# def random_header():
#     user_agents = [
#         'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
#         'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
#         'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
#         'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
#         'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
#         'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
#         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
#         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
#         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
#         'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
#         'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
#     ]
#     return {
#         "User-Agent": random.choice(user_agents),
#         "content-type": "text/plain;charset=UTF-8",
#     }
#
#
# async def fetch_content(url):
#     # await asyncio.sleep(1) 防止请求过快，等待1秒
#     async with aiohttp.ClientSession(
#             headers=random_header(), connector=aiohttp.TCPConnector(ssl=False)
#     ) as session:
#         async with session.get(url) as response:
#             return await response.text()
#
#
# async def parse(url):
#     page = await fetch_content(url)
#     html = etree.HTML(page)
#
#     xpath_movie = '//*[@id="content"]/div/div[1]/ol/li'
#     xpath_title = './/span[@class="title"]'
#     xpath_pages = '//*[@id="content"]/div/div[1]/div[2]/a'
#     xpath_descs = './/span[@class="inq"]'
#     xpath_links = './/div[@class="info"]/div[@class="hd"]/a'
#
#     pages = html.xpath(xpath_pages)
#     fetch_list = []
#     result = []
#
#     for element_movie in html.xpath(xpath_movie):
#         result.append(element_movie)
#
#     for p in pages:
#         fetch_list.append(url + p.get("href"))
#
#     tasks = [fetch_content(url) for url in fetch_list]
#     pages = await asyncio.gather(*tasks)
#
#     for page in pages:
#         html = etree.HTML(page)
#         for element_movie in html.xpath(xpath_movie):
#             result.append(element_movie)
#
#     for i, movie in enumerate(result, 1):
#         title = movie.find(xpath_title).text
#         desc = (
#             "<" + movie.find(xpath_descs).text + ">"
#             if movie.find(xpath_descs) is not None
#             else None
#         )
#         link = movie.find(xpath_links).get("href")
#         print(i, title, desc, link)
#
#
# async def main3():
#     start = time()
#     for i in range(5):
#         await parse(url)
#     end = time()
#     print("Cost {} seconds".format((end - start) / 5))
#
#
# if __name__ == '__main__':
#     asyncio.run(main3())


from lxml import etree
from time import time
import asyncio
import aiohttp

url = "https://movie.douban.com/top250"
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    "content-type": "text/plain;charset=UTF-8",
}


async def fetch_content(url):
    # await asyncio.sleep(1) # 防止请求过快 等待1秒
    async with aiohttp.ClientSession(
        headers=header, connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as response:
            return await response.text()


async def parse(url):
    page = await fetch_content(url)
    html = etree.HTML(page)

    xpath_movie = '//*[@id="content"]/div/div[1]/ol/li'
    xpath_title = './/span[@class="title"]'
    xpath_pages = '//*[@id="content"]/div/div[1]/div[2]/a'
    xpath_descs = './/span[@class="inq"]'
    xpath_links = './/div[@class="info"]/div[@class="hd"]/a'

    pages = html.xpath(xpath_pages)  # 所有页面的链接都在底部获取
    fetch_list = []
    result = []

    for element_movie in html.xpath(xpath_movie):
        result.append(element_movie)

    for p in pages:
        fetch_list.append(url + p.get("href"))  # 解析翻页按钮对应的链接 组成完整后边页面链接

    tasks = [fetch_content(url) for url in fetch_list]  # 并行处理所有翻页的页面
    pages = await asyncio.gather(*tasks)
    # 并发 运行 aws 序列中的 可等待对象。
    # 如果 aws 中的某个可等待对象为协程，它将自动作为一个任务加入日程。
    # 如果所有可等待对象都成功完成，结果将是一个由所有返回值聚合而成的列表。结果值的顺序与 aws 中可等待对象的顺序一致。
    for page in pages:
        html = etree.HTML(page)
        for element_movie in html.xpath(xpath_movie):
            result.append(element_movie)

    for i, movie in enumerate(result, 1):
        title = movie.find(xpath_title).text
        desc = (
            "<" + movie.find(xpath_descs).text + ">"
            if movie.find(xpath_descs) is not None
            else None
        )
        link = movie.find(xpath_links).get("href")
        print(i, title, desc, link)


async def main():
    start = time()
    for i in range(5):
        await parse(url)
    end = time()
    print("Cost {} seconds".format((end - start) / 5))


if __name__ == "__main__":
    asyncio.run(main())
