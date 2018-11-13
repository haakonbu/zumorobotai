class Arbitrator:
    def __init__(self, bbcon):
        self.bbcon = bbcon

    def choose_action(self):
        winning_behavior = None
        max_weight = -1

        # Picks Winner behavior and sends its motor-recommendation tp BBCON
        for behavior in self.bbcon.active_behaviors:
            if behavior.active_flag is True:
                if behavior.weight > max_weight:
                    max_weight = behavior.weight
                    winning_behavior = behavior
        
        return winning_behavior.motor_recommendations, winning_behavior.halt_request
