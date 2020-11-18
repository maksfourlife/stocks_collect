import bs4
import json
import requests
import re
import base64


def expand_url(url, root_url):
    if url[0] == "/":
        return root_url + url[1:]
    return url


def encode_url(url):
    return base64.b64encode(bytes(hex(hash(url)), "utf-8"))


class Loader:
    def __init__(self, websites_file):
        self.websites = {}
        with open(websites_file, "r") as f:
            for website in json.loads(f.read()):
                self.websites[website["url"]] = {k: v for k, v in website.items() if k != "url"}
        self.page_urls = {}

    def load_pages(self):
        with requests.Session() as sess:
            sess.headers.update({'Cache-Control': 'no-cache'})
            for website_url, website in self.websites.items():
                if not (res := sess.get(website_url)).ok:
                    continue
                if website_url not in self.page_urls:
                    self.page_urls[website_url] = []
                for url in re.findall(website["page_pattern"], res.content.decode("utf-8")):
                    url_ = expand_url(url, website_url)
                    self.page_urls[website_url].append((encode_url(url_), url_))

    def get_data(self):
        with requests.Session() as sess:
            sess.headers.update({'Cache-Control': 'no-cache'})
            for website_url, page_urls in self.page_urls.items():
                for (url_key, url) in page_urls:
                    if not (res := sess.get(url)).ok:
                        continue
                    # Ideas
                    # default tags (p, h1, h2, h3, ...)
                    # getting site url by re
                    soup = bs4.BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
                    yield "".join(t.get_text() for t in soup.find_all(self.websites[website_url]["content_tags"]))
