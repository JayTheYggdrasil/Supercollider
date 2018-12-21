import torch
import torch.nn as nn
torch.set_default_tensor_type(torch.DoubleTensor)

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

    def create_input_layer(self, input_formatter):
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_formatter.get_input_state_dimension(), 64))

    def create_hidden_layers(self):
        self.layers.append(nn.Linear(64, 64))
        self.layers.append(nn.Linear(64, 64))
        self.layers.append(nn.Linear(64, 64))

    def create_output_layer(self, output_formatter):
        self.output_size = output_formatter.get_model_output_dimension()
        self.layers.append(nn.Linear(64, self.output_size))
        self.final_activation = nn.Softmax(dim=-1)

    def finalize_model(self, lr=0.1):
        #self.loss=nn.MSELoss()
        self.optimizer=torch.optim.Adam(self.parameters(), lr=lr)

    def loss(self, output, target):
        return torch.mean((output-target)**2)

    def predict(self, arr):
        return self.forward(arr)

    def forward(self, arr):
        for layer in self.layers[:-1]:
            arr=nn.functional.softplus(layer(arr))

        arr=self.layers[-1](arr)
        arr=self.final_activation(arr)
        return arr

    def fit(self, x, target, epochs=1):
        for _ in range(epochs):
            for i in range(len(x)):
                self.optimizer.zero_grad()
                action=self.forward(x[i])
                loss=self.loss(target[i], action)
                loss.backward()
                self.optimizer.step()
        return loss

    def save(self, filepath):
        torch.save(self.state_dict(), filepath)
    def load(self, filepath):
        self.load_state_dict(torch.load(filepath))
