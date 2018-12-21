from bots.base_bot_container import BaseBotContainer

import sys
import os
path = os.path.dirname(__file__) + "\\bots\\"

sys.path.insert(0, path + 'ATBA')
from bots.bots.ATBA.ATBA import ATBA as ATBA
sys.path.insert(0, path)
from bots.bots.testBot import Wavedash

class ATBABotContainer(BaseBotContainer):
    def __init__(self, agent):
        # super init required to contruct bots
        super().__init__(agent)

        #contruct ATBA bot
        self.ATBA = self.initialize_bot(ATBA)
        self.wavedash = self.initialize_bot(Wavedash)
        self.bot_dict = {
            "wavedash": self.wavedash.get_output,
            "stop": self.ATBA.atba_wait,
            "slow": self.ATBA.atba_slow,
            "normal": self.ATBA.atba_normal,
            "fast": self.ATBA.atba_fast,
            "coast": self.ATBA.get_output
        }
        self.make_list()
