import os
import sys
path = os.path.dirname(__file__)
sys.path.insert(0, path)

class ModelBox:
    def __init__(self, num_actions, index, team, load_from = None):
        from machine_learning.input_formatter import InputFormatter
        from machine_learning.output_formatter import OutputFormatter
        from machine_learning.model import Model

        self.input_f = InputFormatter(index, team)
        self.output_f = OutputFormatter(num_actions)

        self.model = Model()

        if load_from == None:
            self.model.create_input_layer(self.input_f)
            self.model.create_hidden_layers()
            self.model.create_output_layer(self.output_f)
            self.model.finalize_model(lr=1e-3)
        else:
            self.model.load(load_from)

    def predict(self, packet=None, replay_tick=None):
        if packet != None:
            data = self.input_f.create_input_array([packet])
        elif replay_tick != None:
            data = self.input_f.create_input_array([replay_tick], gameTick=False)
        else:
            print("Missing Arguments")
            raise SyntaxError

        output = self.model.predict(data)
        output = self.output_f.format_model_output(output)

        return output

    def fit(self, action_index, packets=None, replay_ticks=None):
        target = self.output_f.create_array_for_training(action_index)

        if packets != None:
            data = self.input_f.create_input_array(packets)
        elif replay_ticks != None:
            data = self.input_f.create_input_array(replay_ticks, gameTick=False)
        else:
            print("Missing Arguments")
            raise SyntaxError

        loss = self.model.fit(data, target)
        # print(loss)
    def load(self, filepath):
        self.model.load(filepath)

    def save(self, filepath):
        pass
        #self.model.save(filepath)
