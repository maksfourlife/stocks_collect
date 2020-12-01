class Console:
    def __init__(self):
        self._state_info = {}
        self._objects = {}

    def start(self):
        while True:
            try:
                cmd = input("command >>> ")
                if not cmd:
                    continue
                cmd, *args = cmd.split()
                getattr(self, f"_{cmd}")(*args)
            except Exception as e:
                print(e)

    @staticmethod
    def _hello():
        print("Hello, world!")
