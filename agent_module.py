from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from user_interface import TrainingUI
import time
from inputs import get_key
from RLUtilities.GameInfo import GameInfo

from model_box import ModelBox

class AgentModule:
    def __init__(self, agent, bot_container, model1_path = None, model2_path = None, save_path = None, mode = 0, render = False, ):
        """
        AgentModule.

        agent: The agent that this is running on
        model1_path: Path to load model to be trained from. Defaults to making a new one.
        model2_path: Path to load model to be learned from (Used for transfer learning only).
        save_path: Path to save the model being trained (Used only when mode is not 0). Defaults to not saving.
        mode: 0 - Just playing the game.
              1 - Real time learning from human teacher (Rendering should be enabled).
              2 - Transfer learning from model specified in model2.
        render: Boolean, forced rendering when mode = 1
        """

        self.training_history = [[],[]]
        self.count = 1
        self.ticks_per_update = 60*60 #~60 seconds
        self.save_path = save_path

        model2_bot_num = 0

        self.flags = {
            "render": render or mode == 1,
            "train": mode == 1,
            "transfer": mode == 2
        }

        if self.flags["train"] and self.flags["transfer"]:
            raise Exception("Both train and transfer flags cannot be true.")

        self.info = GameInfo(agent.index, agent.team)
        self.bots = bot_container(agent)
        self.ui = TrainingUI(self.bots)
        self.model = ModelBox(self.bots.num_bots(), agent.index, agent.team)
        self.controls = SimpleControllerState()

        self.reader = None
        if self.flags["train"] or self.flags["transfer"]:
            from keyboard_interface import reader
            self.reader = reader
            self.reader.set_bot_num(self.bots.num_bots())

        if model1_path != None:
            self.model.load(model1_path)

        if self.flags["transfer"]:
            self.model2 = ModelBox(model2_bot_num, agent.index, agent.team)
            if model2_path != None:
                self.model2.load(model2_path)
        self.paused = True



    def get_output(self, packet: GameTickPacket, renderer = None) -> SimpleControllerState:
        self.info.read_packet(packet)
        bot_index = self.model.predict(packet=packet)

        if self.flags["train"] and not self.reader.training_paused:
            self.training_history[0].append(self.reader.intended_index)
            self.training_history[1].append(packet)
            if self.count % self.ticks_per_update == 0:
                self.model.fit(self.training_history[0], packets=self.training_history[1])

        if not self.paused and self.reader.training_paused and self.save_path != None:
            self.model.save(self.save_path)

        if self.flags["transfer"]:
            self.training_history[0].append(self.reader.intended_index)
            self.training_history[1].append(packet)
            if self.count % self.ticks_per_update == 0:
                self.model2.fit(self.training_history[0], packets=self.training_history[1])
            bot_index = self.model2.predict(packet=packet)

        self.count += 1

        if self.flags["render"]:
            if renderer == None:
                raise ValueError("Must specify renderer when rendering is used (mode is 1 or render is true)")
            renderer.begin_rendering()
            if self.reader != None:
                self.ui.update_tick(bot_index, self.reader.intended_index)
                renderer.draw_string_2d(220, 0, 2, 2, "Paused: " + str(self.reader.training_paused), renderer.white())
            else:
                self.ui.update_tick(bot_index, -1)
            self.ui.render(renderer)
            renderer.end_rendering()
        self.paused = self.reader.training_paused
        if self.paused:
            return self.bots.get_bot(index=self.reader.intended_index)(packet)
        return self.bots.get_bot(index=bot_index)(packet)
