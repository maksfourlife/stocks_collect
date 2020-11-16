import json
import requests
import re


def expand_url(url, root_url):
    if url[0] == "/":
        return root_url + url[1:]
    return url


def merge_tags(soup, tag_names):
    return "".join("".join(t.text for t in soup.select(tag)) for tag in tag_names)


class Loader:
    def __init__(self, websites_file):
        with open(websites_file, "r") as f:
            self.websites = json.loads(f)
        self.page_urls = {}

    def load_pages(self):
        with requests.Session:
            for website in self.websites:
                if not (res := requests.get(website["url"])).ok:
                    continue
                for url in re.findall(website["page_pattern"], res.content.decode("utf-8")):
                    url_ = website["url"] + ":" + self.expand_url(url, website_url)
                    self.page_urls[hash(url_)].append(url_)

    def get_data(self):
        with requests.Session:
            for url_hash, url in self.page_urls.values():
                if not (res := requests.get(url)).ok:
                    continue
                soup = BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
                content, time = (merge_tags(soup, website[tags]) for tags in ("content_tags", "time_tags"))
                yield url_hash, (content, parse(re.sub(website["time_replace"], "", time, flags=re.IGNORECASE)))
