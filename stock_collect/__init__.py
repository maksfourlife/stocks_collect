import atexit
import json
import os
from datetime import datetime as dt
from threading import Thread, Lock
from time import sleep

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
        self._counter = 0
        self._lock = Lock()
        self.controller = Controller()
        self._context = {
            "cycle_running": True,
        }
        Thread(target=self._cycle, name="cycle_thread", daemon=True).start()
        if self._config["notificate"] and self.twilio_client:
            Thread(target=self._notificate, name="notification_cycle", daemon=True).start()

    def _notificate(self):
        while True:
            sleep(self._config["notification-interval"] * 3600)
            try:
                self.twilio_client.messages.create(
                    body=f"Hello, Mr. {os.getenv('MR_NOBODY_NAME', 'Nobody')}, loaded {self._counter} words.",
                    from_=self._config["sender"],
                    to=self._config["receiver"])
                with self._lock:
                    self._counter = 0
            except Exception as e:
                print(e)

    def _cycle(self):
        while True:
            if not self._context["cycle_running"]:
                continue
            news = []
            with Loader.create_session() as sess:
                for page in Loader.get_pages(self.websites, sess, Token, self._config["loading-timeout"]):
                    add = Processer.process_news(Loader.load_page(page, sess))
                    with self._lock:
                        self._counter += len(add)
                    news.extend(add)
            News.create(time=dt.now(), news=" ".join(news)).save()
            sleep(self._config["loading-interval"])

    def start(self):
        while True:
            self.controller(self._context)
