from requests import Session
from re import findall, sub
from json import loads, dumps
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from os.path import join


def fetch_page_urls(url, page_pattern, session):
    res = session.get(url)
    if not res.ok:
        return []
    contents = res.content.decode("utf-8")
    return findall(page_pattern, contents)


def merge_tags(soup, tag_names):
    return "".join("".join(t.text for t in soup.select(tag)) for tag in tag_names)


def get_page_data(website, page_url, session):
    res = session.get(page_url)
    if not res.ok:
        return ""
    soup = BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
    content, time = (merge_tags(soup, website[tags]) for tags in ("content_tags", "time_tags"))
    return content, datetime.strptime(time, website["time_format"])


def filter_news(time_lower, time_upper, news):
    return [_news[0] for _news in news if time_lower <= _news[1] <= time_upper]


def dump_news(dumping_folder, news_content, time_stamp):
    """{timestamp: 18:00, content: "Everyone knows Donald Tru...",  TODO: stocks: [...],  TODO: stock_slope: 3.22,}"""
    with open(join(dumping_folder, f"{time_stamp.day}_{time_stamp.month}_{time_stamp.year}.dump"), "a") as f:
        f.write("\n" + dumps({
            "timestamp": f"{time_stamp.hour}:{time_stamp.minute}",
            "content": news_content,
        }))


def get_news(interval, dumping_folder="/dumps"):
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        return print("Unable to load websites")
    pages, dt_now = [], datetime.now()
    with Session() as sess:
        for website in websites:
            urls = fetch_page_urls(website["url"], website["page_pattern"], sess)
            pages.extend(filter_news(dt_now, dt_now + interval, [get_page_data(website, url, sess) for url in urls]))
    dump_news(dumping_folder, " ".join(pages), dt_now)


if __name__ == "__main__":
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        exit()
    news_pages = {}
    with Session() as sess:
        for website in websites:
            pages_urls = fetch_page_urls(website["url"], website["page_pattern"], sess)[:10]
        get_page_data(website, pages_urls[0], sess)
