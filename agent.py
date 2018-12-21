from rlbot.agents.base_agent import BaseAgent
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from agent_module import AgentModule

class TrainingAgent(BaseAgent):
    def initialize_agent(self):
        from bots.ATBA_container import ATBABotContainer as bot_container
        self.agent_module = AgentModule(self, bot_container, mode = 1, save_path = "Saved_Models/Test.pt", render = True)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        return self.agent_module.get_output( packet, self.renderer )
