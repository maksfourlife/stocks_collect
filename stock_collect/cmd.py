import threading


class Cmd:
    commands = {
        "exit": lambda: exit(0),
        "say_hello": lambda: print("hello"),
    }

    def __init__(self):
        threading.Thread(target=self.start, name="Cmd_thread", args=(self,), daemon=True).start()

    def start(self):
        while True:
            print(">>> ")
            self.commands.get((yield), print("No such command."))
