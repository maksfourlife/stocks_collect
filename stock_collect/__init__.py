import peewee
import json
import atexit


class App:
    _config = json.loads("congfig.json")
    connection = {
        "sqlite": peewee.SqliteDatabase,
    }[_config["database"].split(".")[-1]](_config["database"])
    cursor = connection.cursor()
    atexit.register(lambda: connection.close())


from .model import Token, News
