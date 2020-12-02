from time import sleep
from datetime import datetime as dt
from threading import Thread
import os.path as path
import peewee
import json
import atexit


class App:
    dir_path = path.dirname(__file__)
    with open(path.join(dir_path, "config.json"), "r") as _config:
        _config = json.loads(_config.read())
    with open(path.join(dir_path, _config["websites"]), "r") as websites:
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
        self.controller = Controller()
        self._context = {
            "cycle_running": False,
        }
        Thread(target=self._cycle, name="cycle_thread", daemon=True).start()

    def _cycle(self):
        while True:
            if not self._context["cycle_running"]:
                continue
            news_now = News.create(time=dt.now(), news="")
            with Loader.create_session() as sess:
                for page in Loader.get_pages(self.websites, sess, Token, self._config["timeout"]):
                    news_now.news += " ".join(Processer.process_news(Loader.load_page(page, sess)))
                    News.save()
            sleep(self._config["interval"])

    def start(self):
        while True:
            self.controller(self._context)
