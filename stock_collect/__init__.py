from requests import Session
from re import findall, sub
from json import loads, dumps
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from os.path import join
from threading import Timer
from dateparser import parse
from pytz import utc


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
    return content, parse(time)


def filter_news(time_lower, time_upper, news):
    return [_news[0] for _news in news if _news[1] and
            time_lower.timestamp() <= _news[1].timestamp() <= time_upper.timestamp()]


def dump_news(dumping_folder, news_content, time_stamp):
    """{timestamp: 18:00, content: "Everyone knows Donald Tru...",  TODO: stocks: [...],  TODO: stock_slope: 3.22,}"""
    with open(join(dumping_folder, f"{time_stamp.day}_{time_stamp.month}_{time_stamp.year}.dump"), "a+") as f:
        f.write("\n" + dumps({
            "timestamp": f"{time_stamp.hour}:{time_stamp.minute}",
            "content": news_content,
        }))


def fetch(interval, dumping_folder="dumps", start_time=datetime.now()):
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        return print("Unable to load websites")
    pages = []
    with Session() as sess:
        for website in websites:
            urls = fetch_page_urls(website["url"], website["page_pattern"], sess)
            news = [get_page_data(website, url, sess) for url in urls]
            pages.extend(filter_news(start_time, start_time + interval, news))
    dump_news(dumping_folder, " ".join(pages), start_time)


def start_fetching(interval, dumping_folder="dumps", start_time=datetime.now()):
    Timer(interval, start_fetching, args=(interval, dumping_folder, start_time)).start()
    fetch(interval, dumping_folder, start_time)


if __name__ == "__main__":
    fetch(timedelta(hours=1), start_time=datetime.now() - timedelta(hours=1))
