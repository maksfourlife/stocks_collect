import base64
import hashlib
import re
import typing as tp

import bs4
import peewee
import requests
from nltk import wordnet, pos_tag, WordNetLemmatizer
from nltk.corpus import stopwords

from .controller import Controller


class _Session(requests.Session):
    """Session with pre-set parameters."""
    def __init__(self):
        super(_Session, self).__init__()
        self.headers.update({'Cache-Control': 'no-cache'})


class Loader:
    """Implements urls fetching and loading words from pages."""
    @staticmethod
    def create_session() -> _Session:
        """Returns session with pre-set parameters."""
        return _Session()

    @staticmethod
    def _encode_url(url: str) -> str:
        """Turns url into token."""
        return base64.b64encode(hashlib.sha256(url.encode("utf-8")).digest()).decode("utf-8")

    @staticmethod
    def _expand_url(url: str, website_url: str) -> str:
        """Adds domain name to url."""
        lower = website_url.find("//") + 2
        upper = website_url[lower:].find("/") + lower
        website_url = website_url[:upper] + "/"
        if url[0] == "/":
            return website_url + url[1:]
        return url

    @staticmethod
    def get_pages(websites: tp.Iterable[tp.Iterable[str]], session: _Session, token_model: peewee.Model,
                  timeout: int = 5) -> tp.Iterable[tp.Tuple[str, tp.List[str]]]:
        """Fetches page urls from websites' main pages and stores their's tokens."""
        Controller.set_page_loading_state(0, len(websites), 0)
        for i, website in enumerate(websites):
            website_url, page_pattern, *adt = website
            try:
                if not (res := session.get(website_url, timeout=(timeout, timeout))).ok:
                    continue
                for j, url in enumerate(re.findall(page_pattern, res.content.decode("utf-8"))):
                    url = Loader._expand_url(url, website_url)
                    if not token_model.get_or_none(token_model.token == (token := Loader._encode_url(url))):
                        token_model.create(token=token).save()
                        yield url, adt
                        Controller.set_page_loading_state(i + 1, len(websites), j + 1)
            except Exception as e:
                print(e)
        Controller.set_page_loading_state(finished=True)

    @staticmethod
    def load_page(url: str, adt: tp.List[str], session: _Session) -> str:
        """Loads page content."""
        try:
            if not (res := session.get(url)).ok:
                return ""
            soup = bs4.BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
            return " ".join(t.get_text() for t in soup.select(", ".join(["p", "h1", "h2", "h3", "h4", "h5"] + adt)))
        except Exception as e:
            print(e)
            return ""


class Processer:
    """Implements operations for processing raw news data and turning it into word sequances."""
    _ptag_switch = {t: getattr(wordnet.wordnet, u) for t, u in
                    zip(("J", "V", "N", "R"), ("ADJ", "VERB", "NOUN", "ADV"))}
    _stop_words = stopwords.words("english")
    _lem = WordNetLemmatizer()

    @staticmethod
    def count_spaces(s):
        """Counts number of spaces to estimate number of tokens"""
        return len(re.findall("\s+", s))

    @staticmethod
    def _get_ptag(tag: str) -> str:
        """Converts normal tag to wordnet one."""
        for key, item in Processer._ptag_switch.items():
            if tag.startswith(key):
                return item
        return Processer._ptag_switch["N"]

    @classmethod
    def _lemmatize_words(cls, words: tp.Iterable[str]) -> tp.Iterable[str]:
        """Lemmantizes words."""
        return [cls._lem.lemmatize(word, cls._get_ptag(tag)) for word, tag in pos_tag(list(words))]

    @classmethod
    def process_news(cls, news: str) -> tp.Iterable[str]:
        """Takes string of news, splits them, deletes waste and lemmatizes."""
        if not news:
            return []
        pt = re.compile(r"\b([a-zA-Z]+[/\-&][a-zA-Z]+|[a-zA-Z]+|\d{4})\b")
        condition = lambda t: t and t not in cls._stop_words and len(t) > 1
        return cls._lemmatize_words(t for t in pt.findall(news.replace('\xa0', ' ').lower()) if condition(t))
