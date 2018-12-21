from RLUtilities.Maneuvers import AerialTurn, look_at
from RLUtilities.LinearAlgebra import vec3

def aerial_face(car, dir, up = vec3(0, 0, 1)):
        pos = car.pos
        target = look_at(vec3(dir[0], dir[1], dir[2]), up)
        action = AerialTurn(car, target)
        action.step(1/60)
        pitch = action.controls.pitch
        roll = action.controls.roll
        yaw = action.controls.yaw

        return pitch, roll, yaw

def magnitude(vec):
    return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

def direction(vec):
    mag = magnitude( vec )
    if mag == 0:
        return vec
    return vec/mag

def sign(scalar):
    if scalar == 0:
        return 0
    return scalar/abs(scalar)
