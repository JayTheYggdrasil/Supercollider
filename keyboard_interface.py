import threading
from inputs import get_key
class Reader:
    def __init__(self):
        self.codes = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.intended_index = 0
        self.bot_num = 0
        self.training_paused = True
    def set_bot_num(self, bot_num):
        self.bot_num = bot_num
    def update_key(self):
        prefix = "KEY_"
        while True:
            events = get_key()
            for event in events:
                for c in self.codes:
                    if prefix + c == event.code and self.codes.index(c) < self.bot_num:
                        self.intended_index = self.codes.index(c)
                    if prefix + 'LEFTBRACE' == event.code:
                        self.training_paused = False
                    if prefix + 'RIGHTBRACE' == event.code:
                        self.training_paused = True

reader = Reader()
threading.Thread(target=reader.update_key, daemon=True).start()
