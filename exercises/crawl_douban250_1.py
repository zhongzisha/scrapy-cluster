from urllib.request import Request, urlopen
import ssl
from lxml import etree

url = 'https://movie.douban.com/top250'
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    "content-type": "text/plain;charset=UTF-8",
}


def fetch_page(url):
    ret = Request(url, headers=headers)
    response = urlopen(ret)
    return response


def parse(url):
    response = fetch_page(url)
    page = response.read()
    html = etree.HTML(page)

    xpath_movie = '//*[@id="content"]/div/div[1]/ol/li'
    xpath_title = './/span[@class="title"]'
    xpath_pages = '//*[@id="content"]/div/div[1]/div[2]/a'

    pages = html.xpath(xpath_pages)
    fetch_list = []
    result = []

    for element_movie in html.xpath(xpath_movie):
        result.append(element_movie)

    for p in pages:
        fetch_list.append(url + p.get('href'))

    for url in fetch_list:
        response = fetch_page(url)
        page = response.read()
        html = etree.HTML(page)
        for element_movie in html.xpath(xpath_movie):
            result.append(element_movie)

    for i, movie in enumerate(result, 1):
        title = movie.find(xpath_title).text
        print(i, title)


def main():
    parse(url)


if __name__ == '__main__':
    main()
