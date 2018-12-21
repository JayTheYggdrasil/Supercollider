from rlbot.agents.base_agent import BaseAgent
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo

from movement_mechanics.wavedash import wavedash

class Wavedash(BaseAgent):
    def initialize_agent(self):
        self.info = GameInfo(self.index, self.team)
        self.controller = SimpleControllerState()
        self.counter = 0
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        self.renderer.begin_rendering()
        if self.info.my_car.on_ground and not self.info.my_car.jumped and self.counter % 15 == 0:
            self.controller.jump = not self.controller.jump
        else:
            target = self.info.ball.pos
            target[2] = 0
            self.controller, up = wavedash(self.info.my_car, target)
            self.controller.handbrake = True
            self.renderer.draw_line_3d(self.info.my_car.pos, self.info.my_car.pos + up*100, self.renderer.white())
        self.renderer.end_rendering()
        self.counter += 1
        return self.controller
