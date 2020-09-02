from requests import Session
from re import findall, sub
from json import loads
from bs4 import BeautifulSoup


def fetch_pages_urls(url, page_pattern, session):
    res = session.get(url)
    if not res.ok:
        return []
    contents = res.content.decode("utf-8")
    return findall(page_pattern, contents)


def get_page_contents(content_tags, page_url, session):
    res = session.get(page_url)
    if not res.ok:
        return ""
    soup = BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
    content = ''.join(
        (''.join((tag.text for tag in soup.select(content_tag)))) for content_tag in content_tags)
    return content


if __name__ == "__main__":
    with open("websites.json", "r") as f:
        websites = loads(f.read())
    if not websites:
        exit()
    news_pages = {}
    with Session() as sess:
        for website in websites:
            pages_urls = fetch_pages_urls(website["url"], website["page_pattern"], sess)[:10]
            news_pages[website["url"]] = {
                "urls": pages_urls,
                "contents": [get_page_contents(
                    website["content_tags"], url, sess) for url in pages_urls]
            }
    for key, value in news_pages.items():
        print(key)
        print(*value["contents"], sep="\n\n")


