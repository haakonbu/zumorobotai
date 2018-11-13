from camera import *
from irproximity_sensor import *
from ultrasonic import *
from reflectance_sensors import *


class Sensob:
    def __init__(self, sensors):
        self.val = None
        self.sensors = sensors

    def update(self):
        sensor_data = []
        for elem in self.sensors:
            elem.update()
            sensor_data.append(elem.get_value())
        self.process(sensor_data)

    def reset(self):
        for elem in self.sensors:
            elem.reset()

    def process(self, sensor_data):
        self.val = sensor_data[0]

    def get_sensor_value(self):
        return self.val


# Subclasses:

class Camob(Sensob):
    def __init__(self):
        self.camob = Camera()
        super().__init__([self.camob])


class IRProxob(Sensob):
    def __init__(self):
        self.IRProxob = IRProximitySensor()
        super().__init__([self.IRProxob])


class Ultob(Sensob):
    def __init__(self):
        self.ultob = Ultrasonic()
        super().__init__([self.ultob])


class Reflob(Sensob):
    def __init__(self):
        self.Reflob = ReflectanceSensors(True)
        super().__init__([self.Reflob])
