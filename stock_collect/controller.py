import typing as tp


class Controller:
    """Implements operations for controlling and monitoring behavior of application"""
    def __init__(self):
        self._state_info = {}

    def __call__(self, context: tp.Dict[str, object]):
        try:
            cmd = input("command >>> ")
            if not cmd:
                return
            cmd, *args = cmd.split()
            getattr(self, f"_{cmd}")(context, *args)
        except Exception as e:
            print(e)

    @staticmethod
    def _hello(*args):
        print("Hello, world!")
