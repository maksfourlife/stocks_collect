import bs4
import json
import requests
import re
import base64
import time
import threading


class _Session(requests.Session):
    def __init__(self):
        super(_Session, self).__init__()
        self.headers.update({'Cache-Control': 'no-cache'})


class Loader:
    @staticmethod
    def create_session():
        return _Session()

    @staticmethod
    def _encode_url(url):
        return base64.b64encode(bytes(hex(hash(url)), "utf-8"))

    @staticmethod
    def _expand_url(url, website_url):
        if url[0] == "/":
            return website_url + url[1:]
        return url

    @staticmethod
    def get_pages(websites, session, timeout=5):
        for website_url, website in websites.items():
            try:
                if not (res := session.get(website_url, timeout=timeout)).ok:
                    continue
                for url in re.findall(website["page_pattern"], res.content.decode("utf-8")):
                    url = Loader._expand_url(url, website_url)
                    yield url, Loader._encode_url(url)
            except Exception as e:
                print(e)

    @staticmethod
    def load_page(url, session):
        try:
            if not (res := session.get(url)).ok:
                return
            soup = bs4.BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
            return "".join(t.get_text() for t in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5"]))
        except Exception as e:
            print(e)
