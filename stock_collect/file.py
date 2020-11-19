from datetime import datetime, timedelta
from processing import Processer
from os import path
import threading
import time


class IO:
    def __init__(self, directory, interval, loader):
        self.directory = directory
        self.interval = interval
        self.loader = loader
        self.processer = Processer()

    def start(self):
        threading.Thread(target=self._saving_news, name="Saver_thread", daemon=True).start()

    def _get2day_file(self, name, dt=None):
        dt = dt or datetime.now()
        return path.join(self.directory, dt.strftime(f"%Y.%m.%d.{name}.txt"))

    def save_news(self):
        now = datetime.now()
        hashes = repr(now) + "\n" + ",".join(str(t) for t in self.loader.page_urls.keys()) + "\n"
        words = self.processer.process_news(" ".join(self.loader.get_data()))
        for name, content in [("hashes", hashes), ("words", words)]:
            with open(self._get2day_file(name), "a+") as f:
                f.write(content)

    def _saving_news(self):
        """TODO: Should save news as often, as loader says."""
        while True:
            self.save_news()
            time.sleep(self.interval)

    def get_last_hashes(self, max_days=10):
        now = datetime.now()
        for i in range(max_days):
            try:
                with open(self._get2day_file("hash", now + timedelta(days=i)), "r") as f:
                    return set(int(t) for t in f.read().split(","))
            except:
                continue
        return set()
