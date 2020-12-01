import os.path as path
import peewee
import json
import atexit


class App:
    with open(path.join(path.dirname(__file__), "config.json"), "r") as _config:
        _config = json.loads(_config.read())
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
        self._context = {}

    def start(self):
        while True:
            self.controller(self._context)
