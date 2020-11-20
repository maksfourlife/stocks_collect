from datetime import datetime, timedelta
from processing import Processer
from os import path


class IO:
    def __init__(self, directory):
        self.directory = directory
        self.processer = Processer()

    def _get2day_file(self, name, dt=None):
        dt = dt or datetime.now()
        return path.join(self.directory, dt.strftime(f"%Y.%m.%d.{name}.txt"))

    def save_news(self, loader):
        from command import Console
        hashes = ",".join(t.decode("utf-8") for t in loader.page_urls.keys())
        words = []
        Console.INFO["Processing news"] = [0, len(loader.page_urls)]
        for chunk in loader.get_data():
            words.extend(self.processer.process_news(chunk))
            Console.INFO["Processing news"][0] += 1
        words = repr(datetime.now()) + "\n" + " ".join(words)
        for name, content in [("hashes", hashes), ("words", words)]:
            with open(self._get2day_file(name), "a+") as f:
                f.write(content + "\n")

    def get_last_hashes(self, max_days=10):
        now = datetime.now()
        for i in range(max_days):
            try:
                with open(self._get2day_file("hash", now + timedelta(days=i)), "r") as f:
                    return set(int(t) for t in f.read().split(","))
            except:
                continue
        return set()
