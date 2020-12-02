import typing as tp
from threading import Thread


class Controller:
    """Implements operations for controlling and monitoring behavior of application"""
    _state_info = {}

    def __call__(self, context: tp.Dict[str, object]):
        try:
            cmd = input("command >>> ")
            if not cmd:
                return
            cmd, *args = cmd.split()
            getattr(self, f"_{cmd}")(context, *args)
        except Exception as e:
            print(e)

    @classmethod
    def set_state(cls, caller, *args):
        type_, *args = args
        if type_ == "working":
            cls._state_info[caller] = {
                "Processer.get_pages": "Loading website %d of %d, loaded %d pages",
            }[caller] % args
        elif type_ == "done":
            cls._state_info[(caller_cls, caller_func)] += " done!"

    @staticmethod
    def _exit(*args):
        import sys
        sys.exit(0)

    @staticmethod
    def _hello(*args):
        print("Hello, world!")

    @classmethod
    def _info(cls, context):
        print(f"=====INFO======")
        for dict_ in (context, cls._state_info):
            for key, value in dict_.items():
                print(f"{key}: {value}")
        print("===============")

    @staticmethod
    def _cycle(app_context, mode):
        mode = ({"start": True, "stop": False}).get(mode)
        if not mode:
            return print(f"Cycle: no such mode {mode}")
        app_context["cycle_running"] = mode
