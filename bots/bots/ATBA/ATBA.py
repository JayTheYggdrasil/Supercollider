from rlbot.agents.base_agent import BaseAgent
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from RLUtilities.GameInfo import GameInfo
from RLUtilities.Maneuvers import Drive

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

    def atba_fast(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        return self.drive_controls(self.info.ball.pos, target_speed=Speed.fast)

    def atba_normal(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        return self.drive_controls(self.info.ball.pos, target_speed=Speed.normal)

    def atba_slow(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        return self.drive_controls(self.info.ball.pos, target_speed=Speed.slow)

    def atba_wait(self, packet: GameTickPacket) -> SimpleControllerState:
        self.info.read_packet(packet)
        return self.drive_controls(self.info.ball.pos, target_speed=Speed.stop)

    def drive_controls(self, target, target_speed):
        self.action = self.action = Drive(self.info.my_car, target_pos = target, target_speed=target_speed)
        self.action.step(1/60)
        return self.action.controls
