import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats
from random import *


class main(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.car_status = 'none'
        self.jumps = []
        self.average_xy_speed = 0


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #print(difference_angles(Vector2(1, 1).get_angle(), Vector2(-1, 1).get_angle()))
        #return self.controller_state

        self.renderer.begin_rendering()
        self.controller_state.jump = False
        self.controller_state.boost = False
        self.controller_state.handbrake = False
        self.controller_state.throttle = 0
        self.controller_state.steer = 0
        self.controller_state.pitch = -1
  
        jumping(self, packet)
        decide_car_status(self, packet)
        draw(self, packet)
        quickchat.check(self, packet)
        calculate_average_xy_speed(self, packet)
        on_wall_jump(self, packet)
        # run function what car status is
        if self.car_status == 'get_boost':
            get_boost(self, packet)
        if self.car_status == 'kick_ball':
            kick_ball.main(self, packet)
        if self.car_status == 'wrong_side':
            wrong_side(self, packet)
        if self.car_status == 'kickoff':
            kickoff(self, packet)
        if self.car_status == 'clear_ball':
            clear_ball.main(self, packet)

        # If jumps planned stop boosting
        if self.jumps != []:
            self.controller_state.boost = False
        
        self.renderer.end_rendering()
        return self.controller_state

def calculate_average_xy_speed(self, packet):
    self.average_xy_speed -= self.average_xy_speed/100
    self.average_xy_speed += get_xy_speed(self, packet)/100

def get_xy_speed(self, packet):
    my_car = packet.game_cars[self.index]
    car_xy_velocity = Vector2(my_car.physics.velocity.x, my_car.physics.velocity.y)
    car_xy_velocity_magnitude = car_xy_velocity.get_magnitude()
    return car_xy_velocity_magnitude

class quickchat:
    own_goals = 0
    goals = 0
    saves = 0
    opponent_saves = 0
    opponent_own_goals = 0
    opponent_goals = 0
    demolitions = 0
    def check(self, packet):
        my_car = packet.game_cars[self.index]
        opponent = packet.game_cars[abs(self.index-1)]
        if quickchat.goals != my_car.score_info.goals:
            quickchat.goals = my_car.score_info.goals
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_WhatASave)

        if quickchat.saves != my_car.score_info.saves:
            quickchat.saves = my_car.score_info.saves
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Reactions_CloseOne)
        
        if quickchat.opponent_saves != opponent.score_info.saves:
            quickchat.opponent_saves = opponent.score_info.saves
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Reactions_CloseOne)

        if quickchat.opponent_goals != opponent.score_info.goals:
            quickchat.opponent_goals = opponent.score_info.goals
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_NiceShot)

def on_wall_jump(self, packet):
    my_car = packet.game_cars[self.index]
    if my_car.physics.location.z > 1000: double_jump(self, packet)

def draw(self, packet):
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)

    
    # color
    color = self.renderer.create_color(255, 255, 255, 255)
    white_color = self.renderer.create_color(255, 255, 255, 255)
    x = 5
    y = 10
    text_size = 1
    if my_car.team == 0:
        x = 5
        color = self.renderer.create_color(255, 22, 138, 255) # blue
    else:
        x = 150
        color = self.renderer.create_color(255, 255, 127, 80) # orange
        

    # drawing
    self.renderer.draw_string_2d(x, y, text_size, text_size, self.car_status, color)
    self.renderer.draw_string_2d(x, y+10, text_size, text_size, str(Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()), color)
    self.renderer.draw_string_2d(x, y+20, text_size, text_size, 'boost: '+str(my_car.boost), color)
    self.renderer.draw_string_2d(x, y+30, text_size, text_size, 'Jumps: '+str(self.jumps), color)
    self.renderer.draw_string_2d(x, y+40, text_size, text_size, 'Z: '+str(my_car.physics.location.z), color)
    self.renderer.draw_string_2d(x, y+50, text_size, text_size, 'speed: '+str(self.average_xy_speed), color)
    if self.car_status == 'kick_ball': self.renderer.draw_string_2d(x, y+60, text_size, text_size, 'TimeTillHit: '+str(kick_ball.prediction_timer), color)
    if self.car_status == 'clear_ball': self.renderer.draw_string_2d(x, y+60, text_size, text_size, 'TimeTillHit: '+str(clear_ball.prediction_timer), color)

def wrong_side(self, packet):
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    car_direction = get_car_facing_vector(my_car)
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
    goal = get_own_goal(self, packet)

    # double jump if on ground and straight and going good direction
    if self.jumps == [] and my_car.physics.location.z < 17.1 and abs(car_direction.correction_to(goal - car_location)) < 0.1 and my_car.boost > 50: self.controller_state.boost = True
    if self.jumps == [] and my_car.physics.location.z < 17.1 and abs(car_direction.correction_to(goal - car_location)) < 0.1 and not self.controller_state.boost: double_jump(self, packet)
    aim_to(self, packet, goal)
    self.controller_state.throttle = 1.0
    # if in front of the ball+200 reset car status
    if my_car.team == (my_car.physics.location.y-ball_location.y > -2000):
        self.car_status = 'none'

class kick_ball:
    prediction_timer = 0
    ball_prediction = 0
    in_position = False
    def main(self, packet):
        if kick_ball.ball_prediction != 0: ball_location = kick_ball.ball_prediction.physics.location #Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        else: ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        car_direction = get_car_facing_vector(my_car)
        goal = get_opponents_goal(self, packet)
        go_to = car_location
        plus = 0

        kick_ball.prediction_timer -= 1/60
        if kick_ball.prediction_timer < 0: kick_ball.ball_prediction = 0 
        if kick_ball.prediction_timer % 1/car_to_ball_magnitude/100 < 0.001: # if round number update prediction
            time = kick_ball.predict_when_ball_hit(self, packet)
            kick_ball.prediction_timer = time
            kick_ball.ball_prediction = get_ball_prediction(self, int(time*60))
            self.car_status = 'none'
        if kick_ball.ball_prediction == 0:
            self.car_status = 'none'
            kick_ball.in_position = False
            time = kick_ball.predict_when_ball_hit(self, packet)
            kick_ball.prediction_timer = time
            kick_ball.ball_prediction = get_ball_prediction(self, int(time*60))
            

        ball_location = kick_ball.ball_prediction.physics.location
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        # If not in right line with ball and goal Go there.
        ideal_car_location = kick_ball.get_ideal_car_location(self, packet)
        a = [ball_location.x, ball_location.y, 96]
        b = [ideal_car_location.x, ideal_car_location.y, 96]
        self.renderer.draw_line_3d(a, b, own_color(self, packet))
        ideal_ball_to_car_angle = Vector2(ball_location.x - ideal_car_location.x, ball_location.y - ideal_car_location.y).get_angle()
        ball_to_car_angle = Vector2(ball_location.x - car_location.x, ball_location.y - car_location.y).get_angle()
        difference_angle_car_ideal = difference_angles(ideal_ball_to_car_angle, ball_to_car_angle)
        if difference_angle_car_ideal > kick_ball.get_angle_for_goal(self, packet, ball_location) * 2: kick_ball.in_position = False
        car_inline_bool = abs(difference_angle_car_ideal) < kick_ball.get_angle_for_goal(self, packet, ball_location)
        #if my_car.team == 0: print(ideal_ball_to_car_angle, ball_to_car_angle, difference_angle_car_ideal, kick_ball.get_angle_for_goal(self, packet, ball_location))
        # If car not close enough to ideal and car not close to idealLine. Go there
        if Vector2(ideal_car_location.x-car_location.x, ideal_car_location.y-car_location.y).get_magnitude() > 500 and not car_inline_bool and not kick_ball.in_position:
            go_to = ideal_car_location
            plus = -difference_angle_car_ideal/40
            # double jump if on ground and straight and going good direction and far away
            far_away_enough = Vector2(car_location.x-ideal_car_location.x, car_location.y-ideal_car_location.y).get_magnitude() > 1000
            if self.jumps == [] and my_car.physics.location.z < 17.1 and abs(car_direction.correction_to(ideal_car_location - car_location)) < 0.1 and far_away_enough: double_jump(self, packet)
            # draw ideal location
            a = [ideal_car_location.x, ideal_car_location.y, 17]
            self.renderer.draw_rect_3d(a, 40, 40, True, own_color(self, packet))
        # Else head towards the ball
        else:
            kick_ball.in_position = True
            # predict ball location and go there
            #ball_prediction = get_ball_prediction(self, packet, round(car_to_ball_magnitude/50))
            go_to = Vector2(ball_location.x, ball_location.y)
            plus = -difference_angle_car_ideal/15
            # if close to ball stop correcting to line
            #if car_to_ball_magnitude < 500: plus = 0 #-difference_angle_car_ideal/150
            # draw line from car to ball to goal
            a = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
            b = [ball_location.x, ball_location.y, 96]
            inline_with_ball = abs(car_direction.correction_to(Vector2(ball_location.x, ball_location.y) - car_location)) < 0.2
            if car_to_ball_magnitude < my_car.boost*30 and my_car.physics.location.z < 17.1 and self.jumps == [] and inline_with_ball: self.controller_state.boost = True
            if self.jumps == [] and my_car.physics.location.z < 17.1 and car_to_ball_magnitude < 500: double_jump(self, packet)
            self.renderer.draw_line_3d(a, b, self.renderer.create_color(255, 255, 255, 255))


        aim_to(self, packet, go_to, plus)

        # If realy close to ball and good direction Jump
        if car_to_ball_magnitude < 200 and abs(car_direction.correction_to(Vector2(ball_location.x, ball_location.y) - car_location)) < 0.1:
            double_jump(self, packet)
        self.controller_state.throttle = 1.0
        time_needed = time_needed_for_car(self, packet, car_location, ball_location)
        if time_needed < kick_ball.prediction_timer: self.controller_state.throttle = time_needed / kick_ball.prediction_timer

        # if me hit the ball stop kicking the ball
        if packet.game_ball.latest_touch.player_name == my_car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
            self.car_status = 'none'
            kick_ball.ball_prediction = 0
        return self

    def get_angle_for_goal(self, packet, ball_location):
        opponents_goal = get_opponents_goal(self, packet)
        ball_to_pole1 = Vector2(opponents_goal.x+893-ball_location.x, opponents_goal.y-ball_location.y)
        ball_to_pole2 = Vector2(opponents_goal.x-893-ball_location.x, opponents_goal.y-ball_location.y)
        #draw lines
        a = [ball_location.x, ball_location.y, 96]
        b = [ball_to_pole1.x+ball_location.x, ball_to_pole1.y+ball_location.y, 96]
        c = [ball_to_pole2.x+ball_location.x, ball_to_pole2.y+ball_location.y, 96]
        self.renderer.draw_line_3d(a, b, self.renderer.create_color(255, 0, 0, 0))
        self.renderer.draw_line_3d(a, c, self.renderer.create_color(255, 0, 0, 0))
        # return angle
        return abs((ball_to_pole1.get_angle()-ball_to_pole2.get_angle())/2*1.5)

    def get_ideal_car_location(self, packet, ball_location=0):
        if ball_location == 0: ball_location = kick_ball.ball_prediction.physics.location
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        goal = get_opponents_goal(self, packet)
        go_to = car_location
        # If not in right line with ball and goal Go there.
        ball_to_goal_vector = Vector2(ball_location.x - goal.x, ball_location.y - goal.y)
        ball_to_goal_vector = Vector2(goal.x - ball_location.x, goal.y - ball_location.y)
        ball_to_goal_unit_vector = ball_to_goal_vector.unit_vector()
        distance_ball_and_car_needed = kick_ball.get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector)
        ideal_car_location_relative = Vector2(0,0)
        ideal_car_location = Vector2(0,0)
        # if distance bigger than -500 inverse ideal. And kick ball via wall
        if distance_ball_and_car_needed > -1000:
            distance_ball_and_car_needed = 2500
            ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
            ideal_car_location_relative.y *= -1
            ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)
        else:
            ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
            ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)

        return ideal_car_location

    def predict_when_ball_hit(self, packet):
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        sec = 0
        loop = True
        while loop:
            sec += 0.01+sec/12
            ball_location = get_ball_prediction(self, round(sec/60)).physics.location
            car_duration = time_needed_for_car(self, packet, car_location, ball_location)
            if car_duration < sec and ball_location.z < 1000: loop = False
            if sec >= 5.5: loop = False

        return sec

    def get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector):
        
        distance_ball_and_car_needed = -2500
        ball_location = kick_ball.ball_prediction.physics.location
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)
        # https://i.imgur.com/UXvb76k.png

        if ideal_car_location.x > 4096: # sidewall x
            a = abs(4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(4096-ideal_car_location.x)
            distance_ball_and_car_needed += Vector2(a, z).get_magnitude()+400
            distance_ball_and_car_needed
        if ideal_car_location.x < -4096: # sidewall x
            a = abs(-4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(-4096-ideal_car_location.x)
            distance_ball_and_car_needed += Vector2(a, z).get_magnitude()+400
        if ideal_car_location.y > 5120: # backwall y
            a = abs(5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(5120-ideal_car_location.y)
            distance_ball_and_car_needed += Vector2(a, z).get_magnitude()+400
        if ideal_car_location.y < -5120: # backwall y
            a = abs(-5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(-5120-ideal_car_location.y)
            distance_ball_and_car_needed += Vector2(a, z).get_magnitude()+400
        
        return distance_ball_and_car_needed

class clear_ball:
    prediction_timer = 0
    ball_prediction = 0
    in_position = False
    def main(self, packet):
        if clear_ball.ball_prediction != 0: ball_location = clear_ball.ball_prediction.physics.location #Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        else: ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        car_direction = get_car_facing_vector(my_car)
        goal = get_own_goal(self, packet)
        go_to = car_location
        plus = 0

        # when ball is on other side of the field. Stop clearing ball
        self.car_status = 'none'

        clear_ball.prediction_timer -= 1/60
        if clear_ball.prediction_timer < 0: clear_ball.ball_prediction = 0 
        if clear_ball.prediction_timer % 1/car_to_ball_magnitude/100 < 0.001: # if round number update prediction
            time = clear_ball.predict_when_ball_hit(self, packet)
            clear_ball.prediction_timer = time
            clear_ball.ball_prediction = get_ball_prediction(self, int(time*60))
        if clear_ball.ball_prediction == 0:
            time = clear_ball.predict_when_ball_hit(self, packet)
            clear_ball.prediction_timer = time
            clear_ball.ball_prediction = get_ball_prediction(self, int(time*60))
            

        ball_location = clear_ball.ball_prediction.physics.location
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        # If not in right line with ball and goal Go there.
        ideal_car_location = clear_ball.get_ideal_car_location(self, packet)
        a = [ball_location.x, ball_location.y, 96]
        b = [ideal_car_location.x, ideal_car_location.y, 96]
        self.renderer.draw_line_3d(a, b, own_color(self, packet))
        ideal_ball_to_car_angle = Vector2(ball_location.x - ideal_car_location.x, ball_location.y - ideal_car_location.y).get_angle()
        ball_to_car_angle = Vector2(ball_location.x - car_location.x, ball_location.y - car_location.y).get_angle()
        difference_angle_car_ideal = difference_angles(ideal_ball_to_car_angle, ball_to_car_angle)
        car_inline_bool = abs(difference_angle_car_ideal) < 360 - clear_ball.get_angle_for_goal(self, packet, ball_location)
        #if my_car.team == 0: print(ideal_ball_to_car_angle, ball_to_car_angle, difference_angle_car_ideal, clear_ball.get_angle_for_goal(self, packet, ball_location))
        # If car not close enough to ideal and car not close to idealLine. Go there
        # predict ball location and go there
        go_to = Vector2(ball_location.x, ball_location.y)
        #print(': ', car_inline_bool, plus, difference_angle_car_ideal)
        if car_inline_bool: plus = -difference_angle_car_ideal/30
        if car_to_ball_magnitude < 1000: plus = -difference_angle_car_ideal/200
        if car_to_ball_magnitude > 2000: plus = -difference_angle_car_ideal/400
        if my_car.team == 0: self.renderer.draw_string_2d(10, 100, 2, 2, str(plus), self.renderer.create_color(255, 255, 255, 255))
        # draw line from car to ball to goal
        a = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
        b = [ball_location.x, ball_location.y, 96]
        inline_with_ball = difference_angles(Vector2(ball_location.x, ball_location.y).get_angle(), car_location.get_angle()) < 20
        # Use boost. If inline. and ball close to goal
        if abs(packet.game_ball.physics.location.x) < 1000 and abs(packet.game_ball.physics.location.y) > 4000 and car_to_ball_magnitude > 1000 and self.jumps == []: self.controller_state.boost = True
        if self.jumps == [] and my_car.physics.location.z < 17.1 and packet.game_ball.physics.location.z > 200 and inline_with_ball and car_to_ball_magnitude < 500: double_jump(self, packet)
        self.renderer.draw_line_3d(a, b, self.renderer.create_color(255, 255, 255, 255))


        aim_to(self, packet, go_to, plus)

        # If realy close to ball and good direction Jump
        if car_to_ball_magnitude < 200 and abs(car_direction.correction_to(Vector2(ball_location.x, ball_location.y) - car_location)) < 0.1:
            double_jump(self, packet)
        self.controller_state.throttle = 1.0

        # if me hit the ball stop kicking the ball
        if packet.game_ball.latest_touch.player_name == my_car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
            self.car_status = 'none'
            clear_ball.ball_prediction = 0
        return self

    def get_angle_for_goal(self, packet, ball_location):
        opponents_goal = get_own_goal(self, packet)
        ball_to_pole1 = Vector2(opponents_goal.x+893-ball_location.x, opponents_goal.y-ball_location.y)
        ball_to_pole2 = Vector2(opponents_goal.x-893-ball_location.x, opponents_goal.y-ball_location.y)
        #draw lines
        a = [ball_location.x, ball_location.y, 96]
        b = [ball_to_pole1.x+ball_location.x, ball_to_pole1.y+ball_location.y, 96]
        c = [ball_to_pole2.x+ball_location.x, ball_to_pole2.y+ball_location.y, 96]
        self.renderer.draw_line_3d(a, b, self.renderer.create_color(255, 0, 0, 0))
        self.renderer.draw_line_3d(a, c, self.renderer.create_color(255, 0, 0, 0))
        # return angle
        return abs((ball_to_pole1.get_angle()-ball_to_pole2.get_angle())/2*1.5)

    def get_ideal_car_location(self, packet, ball_location=0):
        if ball_location == 0: ball_location = clear_ball.ball_prediction.physics.location
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
        goal = get_own_goal(self, packet)
        go_to = car_location
        # If not in right line with ball and goal Go there.
        ball_to_goal_vector = Vector2(goal.x - ball_location.x, goal.y - ball_location.y)
        ball_to_goal_unit_vector = ball_to_goal_vector.unit_vector()
        distance_ball_and_car_needed = clear_ball.get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector)
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)

        return ideal_car_location

    def predict_when_ball_hit(self, packet):
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        sec = 0
        loop = True
        while loop:
            sec += 0.01+sec/12
            ball_location = get_ball_prediction(self, round(sec/60)).physics.location
            car_duration = time_needed_for_car(self, packet, car_location, ball_location)
            if car_duration < sec and ball_location.z < 400: loop = False
            if sec >= 5.5: loop = False

        return sec

    def get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector):
        
        distance_ball_and_car_needed = 3000
        ball_location = clear_ball.ball_prediction.physics.location
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)
        # https://i.imgur.com/UXvb76k.png

        if ideal_car_location.x > 4096: # sidewall x
            a = abs(4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(4096-ideal_car_location.x)
            distance_ball_and_car_needed -= Vector2(a, z).get_magnitude()+400
            distance_ball_and_car_needed
        if ideal_car_location.x < -4096: # sidewall x
            a = abs(-4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(-4096-ideal_car_location.x)
            distance_ball_and_car_needed -= Vector2(a, z).get_magnitude()+400
        if ideal_car_location.y > 5120: # backwall y
            a = abs(5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(5120-ideal_car_location.y)
            distance_ball_and_car_needed -= Vector2(a, z).get_magnitude()+400
        if ideal_car_location.y < -5120: # backwall y
            a = abs(-5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(-5120-ideal_car_location.y)
            distance_ball_and_car_needed -= Vector2(a, z).get_magnitude()+400
        
        return distance_ball_and_car_needed
def get_car_speed(self, packet):
    my_car = packet.game_cars[self.index]

def aim_to(self, packet, to, plus=0):
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    car_direction = get_car_facing_vector(my_car)
    steer_correction = car_direction.correction_to(to - car_location)
    steer_correction *= -5
    steer_correction += plus
    self.renderer.draw_string_2d(10, 300, 1, 2, str(plus)+' == '+str(steer_correction), own_color(self, packet))


    # Drift if needs to steer much
    if abs(steer_correction) > 7:
        self.controller_state.handbrake = True

    # caps
    if steer_correction > 1:
        steer_correction = 1
    if steer_correction < -1:
        steer_correction = -1

    self.controller_state.steer = steer_correction

def jumping(self, packet):
    # loop trough jumps
    for idx, val in enumerate(self.jumps):
        jump = val-1
        self.jumps[idx] = jump
        # If jump is 0 jump!
        if jump <= 0:
            self.controller_state.jump = True
            self.jumps.remove(jump)

def time_needed_for_car(self, packet, car_from, car_to):
    difference = Vector2(car_from.x-car_to.x, car_from.y-car_to.y)
    length = difference.get_magnitude()
    speed = (self.average_xy_speed+get_xy_speed(self, packet)+1400*8)/10
    if speed == 0: speed = 0.00000000000000001
    duration = length/speed
    return duration

def own_color(self, packet): 
    # get right color
    if packet.game_cars[self.index].team:
        color = self.renderer.create_color(255, 255, 127, 80)
    else:
        color = self.renderer.create_color(255, 22, 138, 255)
    return color

def get_own_goal(self, packet):
    my_car = packet.game_cars[self.index]
    field_info = self.get_field_info()
    goal = Vector2(0, 0)
    if field_info.goals[0].team_num == my_car.team:
        goal = Vector2(field_info.goals[0].location.x, field_info.goals[0].location.y)
    else:
        goal = Vector2(field_info.goals[1].location.x, field_info.goals[1].location.y)
    return goal

def get_opponents_goal(self, packet):
    my_car = packet.game_cars[self.index]
    field_info = self.get_field_info()
    goal = Vector2(0, 0)
    if field_info.goals[0].team_num != my_car.team:
        goal = Vector2(field_info.goals[0].location.x, field_info.goals[0].location.y)
    else:
        goal = Vector2(field_info.goals[1].location.x, field_info.goals[1].location.y)
    return goal

def kickoff(self, packet):
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).get_magnitude()
    plus = 0

    
    self.controller_state.boost = True
    self.controller_state.throttle = 1.0

    # 255.97 and 3840.01
    if abs(car_location.x) < 300:
        if my_car.team: plus = -car_location.x/100
        else: plus = car_location.x/100

    aim_to(self, packet, ball_location, (random()*2-1)+plus, )
    #print(car_location.x, car_location.y)
    # if me hit the ball stop kicking the ball
    if packet.game_ball.latest_touch.player_name == my_car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
        self.car_status = 'none'

    # If realy close to ball Jump
    if car_to_ball_magnitude < 500: double_jump(self, packet)
    # if on wrong side of the ball reset car status
    if my_car.team != (my_car.physics.location.y-ball_location.y > 0):
        self.car_status = 'none'
    return self

def decide_car_status(self, packet):
    my_car = packet.game_cars[self.index]
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)

    # decide car status if none
    if self.car_status == 'none': 
        if my_car.team and (ball_location.y > 1000):
            self.car_status = 'clear_ball'
        elif not my_car.team and (ball_location.y < -1000):
            self.car_status = 'clear_ball'
        elif my_car.team == (my_car.physics.location.y-ball_location.y > 0):
            self.car_status = 'kick_ball'
            kick_ball.ball_prediction = 0
        elif my_car.boost < 50: self.car_status = 'get_boost'
        else: self.car_status = 'wrong_side'
    # if kickoff. Car status kick ball
    if packet.game_info.is_kickoff_pause:
        self.car_status = 'kickoff'
        self.jumps = []

def difference_angles(angle1, angle2):
    angle1 = normalize_angle(angle1)
    angle2 = normalize_angle(angle2)
    difference = angle1 - angle2
    if difference > 180: difference = 360 - difference
    return difference

def is_angle_inbetween(n, a, b):
    n = normalize_angle(n)
    a = normalize_angle(a)
    b = normalize_angle(b)
    if a < b: 
        return a <= n and n <= b
    return a <= n and n <= b

def normalize_angle(angle):
    while angle < 0: angle += 360
    while angle >= 360: angle -= 360
    return angle

def calculate_kick_offset(self, packet):
    
    return self

def get_boost(self, packet):
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    if my_car.boost > 40: self.car_status = 'none'

    closest_boost = get_closest_boost(self, packet)
    #Turn to the boost
    aim_to(self, packet, Vector2(closest_boost.location.x, closest_boost.location.y))
    # If close to the ball. Use Last boost
    if Vector2(car_location.x - closest_boost.location.x, car_location.y - closest_boost.location.y).get_magnitude() < my_car.boost*80:
       self.controller_state.boost = True
    else:
        self.controller_state.boost = False 



    self.controller_state.throttle = 1.0
    # if 100 boost. reset game_status
    if my_car.boost == 100:
        self.car_status = 'none'
    return self

def get_closest_boost(self, packet):
    field_info = self.get_field_info()
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)

    # Get all big boost pads
    count = field_info.num_boosts
    big_pads = []
    for i, pad in enumerate(field_info.boost_pads):
        if i > count:
            break
        if pad.is_full_boost and packet.game_boosts[i].is_active:
            big_pads.append(pad)

    def big_pads_sort_function(e):
        return Vector2(car_location.x - e.location.x, car_location.y - e.location.y).get_magnitude()

    big_pads.sort(key=big_pads_sort_function)
    return big_pads[0]
   
def double_jump(self, packet):
    self.jumps.append(1)
    self.jumps.append(3)
    return self

def get_ball_prediction(self, num):
    ball_prediction = self.get_ball_prediction_struct()
    return ball_prediction.slices[num]
                            
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __truediv__(self, val):
        return Vector2(self.x / val.x, self.y / val.y)
    def multiply(self, val):
        return Vector2(self.x*val, self.y*val)
    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)
    def unit_vector(self):
        magnitude = self.get_magnitude()
        return Vector2(self.x/magnitude, self.y/magnitude)
    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction
    def get_angle(self):
        if self.x == 0: self.x = 0.0000000000000001
        return math.degrees(math.atan2(self.y, self.x))
    def get_magnitude(self): 
        return (self.x ** 2 + self.y ** 2) ** 0.5

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)
