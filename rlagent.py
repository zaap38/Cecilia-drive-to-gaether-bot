import random as rd
import copy as cp

class RLAgent:
    def __init__(self, environment, id=0):
        self.id = id
        self.q = {}
        self.epsilon = 1.0  # exploration
        self.discountEpsilon = 0.99998
        self.gamma = 0.9997  # discount factor
        self.eta = .1  # learning rate

        self.environment = environment

        self.lastReward = 0
        self.lastAction = ""

    def getRandomPolicy(self):
        return rd.choice(self.environment.getLegalActions(self.id))
    
    def getBestPolicy(self, state):
        actions = self.environment.getLegalActions(self.id)

        bestAction = actions[0]
        for a in actions:
            if (state, a) in self.q.keys():
                if (state, bestAction) in self.q.keys():
                    if self.q[state, a] > self.q[state, bestAction]:
                        bestAction = a
                else:
                    bestAction = a

        return bestAction
    
    def getBestPolicyReward(self, state):
        key = (state, self.getBestPolicy(state))
        if key in self.q.keys():
            return self.q[state, self.getBestPolicy(state)]
        return 0
    
    def updateQValues(self, old_state, actionDone, state, reward, final=False):
        if (old_state, actionDone) not in self.q.keys():
            self.q[old_state, actionDone] = 0
        if final:
            self.q[old_state, actionDone] = reward
        else:
            self.q[old_state, actionDone] = (1 - self.eta) * self.q[old_state, actionDone] + self.eta * (reward + \
                    self.getBestPolicyReward(state) * self.gamma)
            self.epsilon = self.epsilon * self.discountEpsilon

    def selectAction(self, state, forceExplore=False, debug=False):
        if rd.random() < self.epsilon:
            return self.getRandomPolicy()
        else:
            return self.getBestPolicy(state)
