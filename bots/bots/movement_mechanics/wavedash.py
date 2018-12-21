from rlbot.agents.base_agent import SimpleControllerState
from RLUtilities.Simulation import Car, Input
from RLUtilities.LinearAlgebra import dot, vec3
from movement_mechanics.utilities import aerial_face, direction, magnitude, sign

def wavedash(car, target):
    controller = SimpleControllerState()
    controller.jump = False

    face = direction(target - car.pos)

    vel = car.vel
    pos = car.pos

    walls = [4096, 5120, 2044]

    dists = []
    for i in range(2):
        if vel[i] < 0:
            d = pos[i] + walls[i]
        elif vel[i] > 0:
            d = pos[i] - walls[i]
        else:
            d = 10000

        dists.append(d)

    times = [abs(dists[0]/vel[0]), abs(dists[1]/vel[1])]

    dist_ciel = walls[2] - pos[2]
    dist_floor = -pos[2]

    accel = -650
    v2 = vel[2]**2
    dists.append(dist_ciel)
    rt = v2 + 2 * accel * dist_ciel
    if rt < 0:
        rt = v2 + 2*accel*dist_floor
        dists[2] = dist_floor
        if rt < 0:
            print("I'm confused")
    times.append(max([(-vel[2] + rt**0.5)/accel, (-vel[2] - rt**0.5)/accel]))

    print(times)

    id = times.index(min(times))
    ups = [vec3(-1, 0, 0), vec3(0, -1, 0), vec3(0, 0, -1)]

    up = ups[id] * sign(vel[id])
    if id == 2:
        up = ups[id] * sign(dist_floor - dist_ciel)

    face = direction(face + up)

    pitch, roll, yaw = aerial_face(car, face, up)
    controller.pitch = pitch
    controller.roll = roll
    controller.yaw = yaw

    flip_dir = car.up() * -1.0
    flip_dir[2] = 0
    flip_dir = direction(dot(flip_dir, car.theta))
    if dists[id] < 100 and times[id] < 0.2:
        controller.jump = True
        controller.pitch = -flip_dir[0]
        controller.roll = 0
        controller.yaw = flip_dir[1]


    return controller, face

def wavedash2(face, up):
    pass
