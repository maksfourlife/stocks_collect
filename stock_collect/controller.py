import typing as tp


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
    def set_page_loading_state(cls, websites=0, total_websites=0, pages=0, finished=False):
        if finished:
            cls._state_info["Loading pages"] += " - done!"
        cls._state_info["Loading pages"] = f"Loading website {websites} of {total_websites}, loaded {pages} pages"

    @staticmethod
    def _exit(*_):
        import sys
        sys.exit(0)

    @staticmethod
    def _hello(*_):
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
