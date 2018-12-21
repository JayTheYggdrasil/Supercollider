from bots.bot_container import BaseBotContainer

class TrainingUI:
    def __init__(self, bot_container: BaseBotContainer):
        self.bot_names = bot_container.get_names()
        self.codes = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.intended_index = 0
        self.current_index = 0

    def render(self, renderer):
        for i in range(len(self.bot_names)):
            color = renderer.white()
            if self.current_index == i:
                color = renderer.red()
            if self.intended_index == i:
                color = renderer.lime()
            renderer.draw_string_2d(10, i * 20, 2, 2, self.codes[i] + " - " + self.bot_names[i], color)

    def update_tick(self, current, intended):
        self.current_index = current
        self.intended_index = intended
