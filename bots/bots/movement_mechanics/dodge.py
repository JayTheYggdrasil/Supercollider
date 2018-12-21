from rlbot.agents.base_agent import BaseAgent
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo
from RLUtilities.Maneuvers import AirDodge

class Speed:
    fast = 2300
    normal = 1400
    slow = 700
    stop = 0

class ATBA(BaseAgent):
    def initialize_agent(self):
        self.info = GameInfo(self.index, self.team)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        return SimpleControllerState()
