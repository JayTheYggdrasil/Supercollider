from bots.base_bot_container import BaseBotContainer

import sys
import os
path = os.path.dirname(__file__) + "\\bots\\"
sys.path.insert(0, path + 'rashBot')
from bots.bots.rashBot.Agent import PythonExample as rashBot
sys.path.insert(0, path + 'Skybot\\Skybot')
from bots.bots.Skybot.Skybot.SkyBot import SkyBot
sys.path.insert(0, path + 'Mork')
from bots.bots.Mork.main import main as Mork

# from rlbot.agents.base_agent import SimpleControllerState
#
# def testFunction(packet):
#     return SimpleControllerState()

class coolBotContainer(BaseBotContainer):
    def __init__(self, agent):
        # super init required to contruct bots
        super().__init__(agent)
        # Construct bots
        self.rashBot = initialize_bot(rashBot)
        self.skybot = initialize_bot(SkyBot)
        self.mork = initialize_bot(Mork)
        # Must set self.bot_dict, the key is what will apear on screen while training
        # the data is a function that recieves only a GameTickPacket and returns a controller state
        # make sure to not put the () on those functions
        self.bot_dict = {
            "rashBot": self.rashBot.get_output,
            "Skybot": self.skybot.get_output,
            "Mork": self.mork.get_output
        }
        # Must end with this
        self.make_list()
