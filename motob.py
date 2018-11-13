from motors import *


class Motob:
    def __init__(self):
        # A list of the motors whose settings will be determined by the motob.
        self.motors = Motors()
        # A holder of the most self.valueent motor recommendation sent to the motob.
        self.value = None

    # Receive a new motor recommendation, load it into the value slot, and operationalize it.
    def update(self, rec):
        self.value = rec
        self.operationalize()

    def operationalize(self):

        if self.value[1] is True:
            self.motors.stop()
        elif self.value[0][0] == "F":
            self.motors.forward(self.value[0][1] * 0.05)
        elif self.value[0][0] == "B":
            self.motors.backward(self.value[0][1] * 0.05)
        elif self.value[0][0] == "L":
            self.motors.left(self.value[0][1] * 0.05)
        elif self.value[0][0] == "R":
            self.motors.right(self.value[0][1] * 0.05)
        elif self.value[0][0] == "S":
            self.motors.stop()
