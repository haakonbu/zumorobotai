import time
from behavior import FollowLine, AvoidCollisions, SnapPhoto, Rotate, Stop, DoCircles
from motob import *
from motors import Motors
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from zumo_button import ZumoButton
from camera import Camera
from arbitrator import Arbitrator


class Bbcontroller:
    def __init__(self):
        self.behaviors = []
        self.active_behaviors = []
        self.sensobs = []
        self.motob = []
        self.arbitrator = None
        self.current_timestep = None
        self.robot = None

    def add_behavior(self, behavior):
        self.behaviors.append(behavior)

    def add_sensob(self):
        self.sensobs.clear()
        for i in range(len(self.active_behaviors)):
            self.sensobs += list((self.active_behaviors[i].sensob))
        self.sensobs = list(set(self.sensobs))

    def add_motob(self, motob):
        self.motob.append(motob)

    def activate_behavior(self):
        for behavior in self.behaviors:
            if (behavior.active_flag is True) and (behavior not in self.active_behaviors):
                self.active_behaviors.append(behavior)

    def deactivate_behavior(self):
        for behavior in self.active_behaviors:
            if behavior.active_flag is False:
                self.active_behaviors.remove(behavior)

    def run_one_timestep(self):
        self.update_all_behaviors()
        print("Active behaviors:\n", *self.active_behaviors, sep="\n")
        print("\n")
        # Arbitrator has a bbcon pointer so the Arbitrator can fetch the
        # relavant data.
        # Returns a tuple of a behavior's motor recommendations and a halt_flag (boolean)
        rec = self.arbitrator.choose_action()
        self.update_all_motobs(rec)
        self.wait(t=None)
        self.reset_all_sensobs()

    def wait(self, t):
        if t is None:
            time.sleep(0.15)
        else:
            time.sleep(t)

    def update_all_sensobs(self):
        self.add_sensob()
        for i in range(len(self.sensobs)):
            self.sensobs[i].update()

    def reset_all_sensobs(self):
        for i in range(len(self.sensobs)):
            # Need a sensob reset method. We do not want to access
            # sensob's value directly.
            for j in range(len(self.active_behaviors)):
                if self.sensobs[i] in self.active_behaviors[j].sensob:
                    self.sensobs[i].reset()
        for i in range(len(self.motob)):
            self.motob[i].update((["F", 0], False))

    def update_all_behaviors(self):
        for i in range(len(self.behaviors)):
            if self.behaviors[i].active_flag is True:
                self.behaviors[i].update()
        self.activate_behavior()
        self.deactivate_behavior()

    # Tuple of a behavior's motor recommendations and a halt_flag (boolean)
    # We will update all motobs which will then update the settings
    # for all motors.
    def update_all_motobs(self, tuple):
        print(tuple)
        for i in range(len(self.motob)):
            # Motob can also check the halt_flag
            self.motob[i].update(tuple)


if __name__ == '__main__':
    bbcon = Bbcontroller()
    arbitrator = Arbitrator(bbcon)

    zumo = ZumoButton()
    zumo.wait_for_press()

    r = ReflectanceSensors()
    u = Ultrasonic()
    c = Camera()

    sensobs = [r, u, c]
    bbcon.arbitrator = arbitrator

    fl = FollowLine(bbcon, sensobs)
    ac = AvoidCollisions(bbcon, sensobs)
    sp = SnapPhoto(sensobs)
    ro = Rotate(sensobs)
    st = Stop(bbcon, sensobs)
    dc = DoCircles(sensobs)

    bbcon.add_behavior(dc)
    bbcon.add_behavior(fl)
    bbcon.add_behavior(ac)
    bbcon.add_behavior(sp)
    bbcon.add_behavior(ro)
    bbcon.add_behavior(st)

    bbcon.add_sensob()
    motob = Motob()
    bbcon.add_motob(motob)

    print("BBController initalized")
    print("Behaviors:\n", *bbcon.behaviors, sep="\n")
    print("\nSensobs:\n", *bbcon.sensobs, sep="\n")
    print("\nMotobs:\n", *bbcon.motob, sep="\n")

    while True:
        bbcon.run_one_timestep()
        print(u.sensor_get_value())
