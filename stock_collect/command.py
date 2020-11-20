from file import IO
from processing import Processer
from loading import Loader


class Console:
    INFO = {}

    def __init__(self):
        self.processer = Processer()
        self.loader = None
        self._commands = {
            "hello": lambda: print("Hello, world"),
            "init_loader": lambda a0, a1, a2: setattr(self, "loader", Loader(a0, a1, int(a2))),
            "start_loader": lambda: print("Loader not init.") if self.loader is None else self.loader.start(),
            "info": lambda: [print(k, v) for k, v in self.INFO.items()],
        }

    def start(self):
        while True:
            args = input(">>> ").split()
            if len(args):
                command, *args = args
            else:
                continue
            if command == "exit":
                return
            self._commands.get(command, lambda: print(f"No such command: {command}"))(*args)
