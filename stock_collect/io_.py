import base64
import re
import typing as tp
import peewee

import bs4
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
        return base64.b64encode(bytes(hex(hash(url)), "utf-8"))

    @staticmethod
    def _expand_url(url: str, website_url: str) -> str:
        """Adds domain name to url."""
        if url[0] == "/":
            return website_url + url[1:]
        return url

    @staticmethod
    def get_pages(websites: tp.Iterable[tp.Iterable[int]], session: _Session, token_model: peewee.Model,
                  timeout: int = 5) -> tp.Generator[None, tp.Union[tp.Tuple[str, str], None], None]:
        """Fetches page urls from websites' main pages and stores their's tokens."""
        Controller.set_page_loading_state(0, len(websites), 0)
        for i, website in enumerate(websites):
            website_url, page_pattern, *_ = website.values()
            try:
                if not (res := session.get(website_url, timeout=timeout)).ok:
                    continue
                for j, url in enumerate(re.findall(page_pattern, res.content.decode("utf-8"))):
                    url = Loader._expand_url(url, website_url)
                    if token_model.get_or_none(token_model.token == (token := Loader._encode_url(url))) is None:
                        token_model.create(token=token).save()
                        yield url
                        Controller.set_page_loading_state(i + 1, len(websites), j + 1)
            except Exception as e:
                print(e)
        Controller.set_page_loading_state(finished=True)

    @staticmethod
    def load_page(url: str, session: _Session) -> tp.Union[str, None]:
        """Loads page content."""
        try:
            if not (res := session.get(url)).ok:
                return
            soup = bs4.BeautifulSoup(res.content.decode("utf-8"), features="html.parser")
            return " ".join(t.get_text() for t in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5"]))
        except Exception as e:
            print(e)


class Processer:
    """Implements operations for processing raw news data and turning it into word sequances."""
    _ptag_switch = {t: getattr(wordnet.wordnet, u) for t, u in
                    zip(("J", "V", "N", "R"), ("ADJ", "VERB", "NOUN", "ADV"))}
    _stop_words = stopwords.words("english")
    _lem = WordNetLemmatizer()

    @staticmethod
    def _get_ptag(tag: str) -> str:
        """Converts normal tag to wordnet one."""
        for key, item in Processer._ptag_switch.items():
            if tag.startswith(key):
                return item
        return Processer._ptag_switch["N"]

    @classmethod
    def _lemmatize_words(cls, words: tp.Iterable[str]) -> tp.Generator[None, tp.Tuple[str, str], None]:
        """Lemmantizes words."""
        return (cls._lem.lemmatize(word, cls._get_ptag(tag)) for word, tag in pos_tag(list(words)))

    @classmethod
    def process_news(cls, news: str) -> tp.Iterable[str]:
        """Takes string of news, splits them, deletes waste and lemmatizes."""
        if not news:
            return []
        pt = re.compile(r"\b([a-zA-Z]+[/\-&][a-zA-Z]+|[a-zA-Z]+|\d{4})\b")
        condition = lambda t: t and t not in cls._stop_words and len(t) > 1
        return cls._lemmatize_words(t for t in pt.findall(news.replace('\xa0', ' ').lower()) if condition(t))
