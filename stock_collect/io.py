from datetime import datetime
from os import path
import threading
import time


class IO:
    def __init__(self, directory, interval, loader):
        self.directory = directory
        self.interval = interval
        self.loader = loader
        threading.Thread(target=self.save_news, name="DumperThread", args=(self,), daemon=True).start()

    def get2day_file(self, name):
        return path.join(self.directory, now.strftime(f"%Y.%m.%d.{name}.txt"))

    def save_news(self):
        while True:
            now = datetime.now()
            hashes = ",".join(str(t) for t in self.loader.page_urls.keys())
            words = ""
            for name, content in [("hashes", hashes), ("words", words)]:
                with open(self.get2day_file(name), "a+") as f:
                    f.write("T:%s;\nH:%s;\n" % (now, content))
            time.sleep(self.interval)

    def get_last_hashes(self):
        try:
            with open(self.get2day_file("hashes"), "r") as f:
                return set([int(t) for t in f.read().split(";\n")[-2].split(",")])
        except:
            return set()
