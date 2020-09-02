from requests import Session
from re import compile
from json import loads


def get_news_pages(website):
    assert list(website.keys()) == ["url", "page_pattern", "content_tags", "time_tags"]
    with Session() as sess:
        res = sess.get(website["url"])
        if not res.ok:
            return []
        contents = res.content.decode("utf-8")
        page_pattern = compile(website["page_pattern"])
        return page_pattern.findall(contents)


if __name__ == "__main__":
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        exit()
    news_pages = {}
    for website in websites:
        news_pages[website["url"]] = get_news_pages(website)
    print(news_pages)
