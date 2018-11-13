import imager2 as IMR
import random
import wiringpi as wp
from motors import Motors
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from zumo_button import ZumoButton
from camera import Camera


class Behavior:
    def __init__(self, bbcon, sensob):
        self.bbcon = bbcon  # Pointer to the Behavior Based Controller
        self.sensob = sensob  # Filled by subclass
        self.motor_recommendations = []  # Motobs, filled by subclass
        self.active_flag = False  # Not active unless initiated
        self.halt_request = False  # Halt request is set to True when behavior wants to halt robot
        self.priority = 1  # Priority will be filled by subclass
        self.match_degree = 0  # Will be updated regularly
        self.weight = 0  # Will be updated regularly

        self.speed = 0.2

    def consider_deactivation(self):
        raise NotImplementedError()

    def consider_activation(self):
        raise NotImplementedError()

    def update(self):
        self.update_activity_status()
        self.sense_and_act()
        self.weight = self.match_degree * self.priority

    def sense_and_act(self):
        raise NotImplementedError()

    def update_activity_status(self):
        if self.active_flag:
            if self.consider_deactivation():
                self.active_flag = False
        if not self.active_flag:
            if self.consider_activation():
                self.active_flag = True


class FollowLine(Behavior):
    def __init__(self, bbcon, sensob):
        super(FollowLine, self).__init__(bbcon, sensob)

    def consider_deactivation(self):
        if self.sensob[1].sensor_get_value() <= 10:
            return True
        return False

    def consider_activation(self):
        if sum(self.sensob[0].update()) >= 2500:
            return True
        return False

    def sense_and_act(self):
        self.sensob[1].update()
        if self.sensob[1].sensor_get_value() <= 10:
            self.match_degree = 0

        reflectance = self.sensob[0].update()
        highest = 0  # Set led 0 by default. Updated in for loop
        for i in range(len(reflectance)):
            if reflectance[i] > reflectance[highest]:
                highest = i

        if highest == 0:
            self.motor_recommendations = ['R', 30]
            self.match_degree = 1

        elif highest == 1:
            self.motor_recommendations = ['R', 15]
            self.match_degree = 0.8

        elif highest == 2 or highest == 3:
            self.motor_recommendations = ['F', 10]
            self.match_degree = 0.5

        elif highest == 4:
            self.motor_recommendations = ['L', 15]
            self.match_degree = 0.8

        elif highest == 5:
            self.motor_recommendations = ['L', 30]
            self.match_degree = 1


class AvoidCollisions(Behavior):
    def __init__(self, bbcon, sensob):
        super(AvoidCollisions, self).__init__(bbcon, sensob)

    def consider_deactivation(self):
        if self.sensob[1].sensor_get_value() > 10:
            return True
        return False

    def consider_activation(self):
        if self.sensob[1].sensor_get_value() <= 10:
            return True
        return False

    def sense_and_act(self):
        self.sensob[1].update()
        if self.sensob[1].sensor_get_value() <= 10:
            self.match_degree = 1
            self.halt_request = True


class SnapPhoto(Behavior):
    def __init__(self, sensob):
        super(SnapPhoto, self).__init__(None, sensob)
        self.im = None

    def consider_deactivation(self):
        if self.sensob[2].value is not None:
            return True
        return False

    def consider_activation(self):
        if self.halt_request and (self.sensob[2].value is None):
            return True
        return False

    def sense_and_act(self):
        if self.halt_request and (self.sensob[2].value is None):
            self.im = IMR.Imager(self.sensob[2].update()).scale(1, 1)
            self.match_degree = 0
        elif self.sensob[2].value is None and not self.halt_request:
            self.match_degree = 0
        elif self.sensob[2].value is not None:
            self.match_degree = 0


class Rotate(Behavior):
    def __init__(self, sensob):
        super(Rotate, self).__init__(None, sensob)

    def consider_deactivation(self):
        if sum(self.sensob[0].update()) < 1:
            return True
        return False

    def consider_activation(self):
        if self.sensob[1].sensor_get_value() <= 10:
            return True
        return False

    def sense_and_act(self):
        if self.sensob[1].sensor_get_value() <= 20:
            self.motor_recommendations = ['B', 10]
            self.match_degree = 0.7
        else:
            self.motor_recommendations = ['L', 20]
            self.match_degree = 1


class Stop(Behavior):
    def __init__(self, bbcon, sensob):
        super(Stop, self).__init__(bbcon, sensob)

    def consider_deactivation(self):
        if sum(self.sensob[0].update()) > 1:
            return True
        return False

    def consider_activation(self):
        if sum(self.sensob[0].update()) < 0.1:
            return True
        return False

    def sense_and_act(self):
        if sum(self.sensob[0].update()) <= 0.1:
            self.match_degree = 1
            self.halt_request = True


class DoCircles(Behavior):
    def __init__(self, sensob):
        super(DoCircles, self).__init__(None, sensob)
        self.active_flag = True

    def consider_deactivation(self):
        if sum(self.sensob[0].update()) < 1 or self.sensob[1].sensor_get_value() <= 10:
            return True
        return False

    def consider_activation(self):
        return None

    def sense_and_act(self):
        dir = random.choice(['F', 'B', 'L', 'R'])
        self.motor_recommendations = [dir, 10]

        if sum(self.sensob[0].update()) < 1 or self.sensob[1].sensor_get_value() <= 10:
            self.match_degree = 0
        else:
            self.match_degree = 1
