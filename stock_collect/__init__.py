from requests import Session
from re import findall, sub
from json import loads, dumps
from datetime import datetime
from bs4 import BeautifulSoup
from os.path import join


def fetch_page_urls(url, page_pattern, session):
    res = session.get(url)
    if not res.ok:
        return []
    contents = res.content.decode("utf-8")
    return findall(page_pattern, contents)


def get_page_contents(website, page_url, session):
    res = session.get(page_url)
    if not res.ok:
        return ""
    soup = BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
    content = ''.join(
        ''.join(tag.text for tag in soup.select(content_tag)) for content_tag in website["content_tags"])
    time = "".join(
        "".join(t.text for t in soup.select(time_tag)) for time_tag in website["time_tags"])
    time = datetime.strptime(time, website["time_format"])
    return content, time


def dump_news(news_content, dumping_folder):
    """{timestamp: 18:00, content: "Everyone knows Donald Tru...",  TODO: stocks: [...],  TODO: stock_slope: 3.22,}"""
    dt_now = datetime.now()
    with open(join(dumping_folder, f"{dt_now.day}_{dt_now.month}_{dt_now.year}.dump"), "a") as f:
        f.write("\n" + dumps({
            "timestamp": f"{dt_now.hour}:{dt_now.minute}",
            "content": news_content,
        }))


if __name__ == "__main__":
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        exit()
    news_pages = {}
    with Session() as sess:
        for website in websites:
            pages_urls = fetch_page_urls(website["url"], website["page_pattern"], sess)[:10]
    #         news_pages[website["url"]] = {
    #             "urls": pages_urls,
    #             "contents": [get_page_contents(
    #                 website["content_tags"], url, sess) for url in pages_urls]
    #         }
    # for key, value in news_pages.items():
    #     dump_news(" ".join(value["contents"]), "dumps")
        get_page_contents(website, pages_urls[0], sess)
