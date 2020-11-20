import bs4
import json
import requests
import re
import base64
import time
import threading

from file import IO


def _expand_url(url, root_url):
    if url[0] == "/":
        return root_url + url[1:]
    return url


def _encode_url(url):
    return base64.b64encode(bytes(hex(hash(url)), "utf-8"))


class Loader:
    def __init__(self, websites_file, directory, interval):
        self.interval = interval
        self.saver = IO(directory)
        self.websites = {}
        with open(websites_file, "r") as f:
            for website in json.loads(f.read()):
                self.websites[website["url"]] = {k: v for k, v in website.items() if k != "url"}
        self.page_urls = {}

    def start(self):
        threading.Thread(target=self._loop, name="LoaderThread", daemon=True).start()

    def _loop(self):
        while True:
            self.load_pages()
            self.saver.save_news(self)
            time.sleep(self.interval)

    def load_pages(self, timeout=5):
        url_keys = self.saver.get_last_hashes()
        with requests.Session() as sess:
            sess.headers.update({'Cache-Control': 'no-cache'})
            for website_url, website in self.websites.items():
                try:
                    if not (res := sess.get(website_url, timeout=timeout)).ok:
                        continue
                    for url in re.findall(website["page_pattern"], res.content.decode("utf-8")):
                        url = _expand_url(url, website_url)
                        if (key := _encode_url(url)) not in url_keys:
                            self.page_urls[key] = url
                except:
                    continue

    def get_data(self):
        with requests.Session() as sess:
            sess.headers.update({'Cache-Control': 'no-cache'})
            for _, url in self.page_urls.items():
                try:
                    if not (res := sess.get(url)).ok:
                        continue
                    soup = bs4.BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
                    yield "".join(t.get_text() for t in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5"]))
                except:
                    continue
