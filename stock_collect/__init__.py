import atexit
import json
import os
from datetime import datetime as dt
from threading import Thread, Lock
from time import sleep
import re

import peewee
from twilio.rest import Client


class App:
    dir_path = os.path.dirname(__file__)
    with open(os.path.join(dir_path, "config.json"), "r") as _config:
        _config = json.loads(_config.read())
    with open(os.path.join(dir_path, _config["websites"]), "r") as websites:
        websites = json.loads(websites.read())
    connection = {
        "sqlite": peewee.SqliteDatabase,
    }[_config["database"].split(".")[-1]](_config["database"])
    cursor = connection.cursor()
    atexit.register(lambda: App.connection.close())


from .model import Token, News
from .controller import Controller
from .io_ import Loader, Processer


class App(App):
    def __init__(self):
        self.twilio_client = None
        if sid := os.getenv("TWILIO_ACCOUNT_SID"):
            if token := os.getenv("TWILIO_AUTH_TOKEN"):
                self.twilio_client = Client(sid, token)
        self.phones = {t: os.getenv(f"{t.upper()}_PHONE") for t in ("receiver", "sender")}
        self._lock = Lock()
        self.controller = Controller()
        self._context = {
            "cycle running": True,
            "total words": 0
        }
        Thread(target=self._cycle, name="cycle_thread", daemon=True).start()
        if self._config["notificate"] and self.twilio_client and all(self.phones.values()):
            Thread(target=self._notificate, name="notification_cycle", daemon=True).start()
        else:
            print("Notifications not avaible!")

    def _notificate(self):
        while True:
            sleep(self._config["notification-interval"])
            try:
                self.twilio_client.messages.create(
                    body=f"Hello, Mr. {os.getenv('MR_NOBODY_NAME', 'Nobody')}, "
                         f"loaded {self._context['total words']} words.",
                    from_=self.phones["sender"],
                    to=self.phones["receiver"])
                with self._lock:
                    self._context["total words"] = 0
            except Exception as e:
                print(e)

    def _get_batched_size(self, news_):
        if self._config["preprocess"]:
            return len(news_)
        else:
            return sum(Processer.count_spaces(t) for t in news_)

    def _add_batch(self, add, news_):
        if self._config["preprocess"]:
            add = Processer.process_news(add)
            length = len(add)
            news_.extend(add)
        else:
            length = Processer.count_spaces(add)
            news_.append(add)
        with self._lock:
            self._context["total words"] += length

    def _cycle(self):
        while True:
            if not self._context["cycle running"]:
                continue
            news = News.create(time=dt.now(), news="")
            news.save()
            news_ = []
            with Loader.create_session() as sess:
                for url, adt in Loader.get_pages(self.websites, sess, Token, self._config["loading-timeout"]):
                    self._add_batch(Loader.load_page(url, adt, sess), news_)
                    if self._get_batched_size(news_) >= self._config["batch-size"]:
                        news.news += " ".join(news_) + " "
                        news.save()
                        news_.clear()
            news.news += " ".join(news_) + " "
            news.save()
            sleep(self._config["loading-interval"])

    def start(self):
        while True:
            self.controller(self._context)
