class BaseBotContainer:
    def __init__(self, agent):
        self.name = agent.name
        self.team = agent.team
        self.index = agent.index
        self.renderer = agent.renderer
        self.get_field_info = agent.get_field_info
        self.get_ball_prediction_struct = agent.get_ball_prediction_struct

    def initialize_bot(self, bot_class):
        return self.initialize_agent(bot_class, self.name, self.team, self.index, self.renderer, self.get_field_info, self. get_ball_prediction_struct)

    def make_list(self):
        self.bot_list = [self.bot_dict[key] for key in self.bot_dict]

    def index_of(self, bot):
        self.bot_list.index(bot)

    def get_bot(self, key=None, index=None):
        if type(key) != type(None):
            return self.bot_dict[key]
        elif type(index) != type(None):
            return self.bot_list[index]

    def get_names(self):
        names = []
        for name in self.bot_dict:
            names.append(name)
        return names

    def num_bots(self):
        return len(self.bot_list)

    def initialize_agent(self, agent_class, name, team, index, renderer, get_field_info, get_ball_prediction_struct):
        agent = agent_class(name, team, index)
        agent.renderer = renderer
        agent.get_field_info = get_field_info
        agent.get_ball_prediction_struct = get_ball_prediction_struct
        agent.initialize_agent()
        return agent
