import torch
import math
torch.set_default_tensor_type(torch.DoubleTensor)

class InputFormatter:
    def __init__(self, index, team):
        self.index = index
        self.team = team
        car_norm = [[4096, 5120, 2044],  # car pos
                   [2300, 2300, 2300],  # car velocity
                   [math.pi, math.pi, math.pi], # car rotation
                   [5.5, 5.5, 5.5]] # car angular velocity

        ball_norm = [[4906, 5120, 2044],  # ball pos
                    [4500, 4500, 4500],  # ball velocity
                    [6, 6, 6]]  # ball angular velocity

        self.normilization = torch.Tensor(car_norm + car_norm + ball_norm)

    def create_input_array(self, input_data, gameTick=True, batch_num=1):
        data = []
        for d in input_data:
            data.append( self.create_input(d, gameTick=gameTick) )
        return torch.stack(data)

    def get_closest_car(self, input_data, gameTick=True):
        if gameTick:
            ball = input_data.game_ball.physics
            d = ball.location
            ball_pos = torch.Tensor([d.x, d.y, d.z])
            closest = None
            distance = 9999999
            for index in range(len(input_data.game_cars)):
                if index == self.index:
                    continue
                car = input_data.game_cars[index]
                d = car.physics.location
                car_pos = torch.Tensor([d.x, d.y, d.z])
                dist = torch.sum((ball_pos - car_pos)**2)**0.5
                if dist < distance:
                    distance = dist
                    closest = car

            return self.get_car_data(closest)
        else:
            raise NotImplementedError

    def get_car_data(self, _car):
        car = _car.physics
        d = car.location
        car_pos = torch.Tensor([d.x, d.y, d.z])
        d = car.velocity
        car_vel = torch.Tensor([d.x, d.y, d.z])
        d = car.rotation
        car_rot = torch.Tensor([d.roll, d.yaw, d.pitch])
        d = car.angular_velocity
        car_avel = torch.Tensor([d.x, d.y, d.z])
        return car_pos, car_vel, car_rot, car_avel

    def create_input(self, input_data, gameTick=True):
        if gameTick:
            car_pos, car_vel, car_rot, car_avel = self.get_car_data(input_data.game_cars[self.index])
            closest_pos, closest_vel, closest_rot, closest_avel = self.get_closest_car(input_data, gameTick=True)

            ball = input_data.game_ball.physics
            d = ball.location
            ball_pos = torch.Tensor([d.x, d.y, d.z])
            d = ball.velocity
            ball_vel = torch.Tensor([d.x, d.y, d.z])
            d = ball.angular_velocity
            ball_avel = torch.Tensor([d.x, d.y, d.z])

            #Other stats
            other = input_data.game_cars[self.index]

            stats = torch.Tensor([
                other.boost/100,
                1 if other.has_wheel_contact else -1,
                1 if other.is_super_sonic else -1,
                1 if other.jumped else -1,
                1 if other.double_jumped else 1,
            ])
        else:
            raise NotImplementedError()

        spatial = torch.stack([car_pos, car_vel, car_rot, car_avel, closest_pos, closest_vel, closest_rot, closest_avel, ball_pos, ball_vel, ball_avel])
        if self.team == 1:
            spatial[:, 1] *= -1
        if car_pos[0] < 0:
            spatial[:, 0] *= -1

        spatial = spatial/self.normilization

        flat_spatial = spatial.view(33)

        output = torch.cat( [flat_spatial, stats] )

        return output

    def get_input_state_dimension(self):
        return 38
