import Bot
from rlbot.agents.base_agent import BaseAgent


class PythonExample(BaseAgent):

    def get_output(self, packet):

        game = self.convert_packet_to_v3(packet)
        output = Bot.Process(self, game)

        return self.convert_output_to_v4(output)


class Agent:

    def __init__(self, name, team, index):
        self.index = index

    def get_output_vector(self, game):
        return Bot.Process(self, game)


class agent:

    def __init__(self, index):
        self.index = index

    def get_output_vector(self, game):
        return Bot.Process(self, game.GameTickPacket, 2)
