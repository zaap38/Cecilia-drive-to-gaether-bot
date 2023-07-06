import random as rd
import copy as cp

class RLAgent:

    def __init__(self) -> None:
        self.id = 0
        self.q = {}
        self.epsilon = 1.0  # exploration
        self.discountEpsilon = 0.995
        self.gamma = 0.1  # discount factor
        self.eta = 0.05  # learning rate
        self.legalActions = []

    def getRandomPolicy(self, state):
        return rd.choice(self.getLegalActions(state))
    
    def getLegalActionRewards(self, state):
        couples = []
        actions = self.getLegalActions(state)
        for a in actions:
            if (state, a) in self.q.keys():
                couples.append((a, self.q[state, a]))
            else:
                couples.append((a, 0))
        return str(couples)
    
    def getBestPolicy(self, state):
        bestAction = 0
        actions = self.getLegalActions(state)
        for a in actions:
            if (state, a) in self.q.keys():
                if (state, bestAction) in self.q.keys():
                    if self.q[state, a] > self.q[state, bestAction]:
                        bestAction = a
                else:
                    bestAction = a
        return bestAction
    
    def getBestPolicyReward(self, state):
        bestAction = 0
        actions = self.getLegalActions(state)
        for a in actions:
            if (state, a) in self.q.keys():
                if (state, bestAction) in self.q.keys():
                    if self.q[state, a] > self.q[state, bestAction]:
                        bestAction = a
                else:
                    bestAction = a
        if (state, bestAction) not in self.q.keys():
            return 0
        return self.q[state, bestAction]
    
    def updateQValues(self, old_state, actionDone, state, reward):
        #print(self.q)
        if (old_state, actionDone) not in self.q.keys():
            self.q[old_state, actionDone] = 0
        old_reward = self.q[old_state, actionDone]
        self.q[old_state, actionDone] += self.eta * (reward + \
                (self.getBestPolicyReward(state) - self.q[old_state, actionDone]) * self.gamma)
        if abs(old_reward - self.q[old_state, actionDone]) <= 0.05:
            self.epsilon = self.epsilon * self.discountEpsilon

    def getLegalActions(self, state):
        return self.legalActions

    def selectAction(self, state):
        if rd.random() < self.epsilon:  # explore
            action = self.getRandomPolicy(state)
        else:  # best policy
            action = self.getBestPolicy(state)
        return action

class TestEnv:

    def __init__(self) -> None:
        self.agent = RLAgent()

    def getReward(self, state, action):
        return 1 if action == state else 0
    
    def getLegalActions(self, state):
        return [0, 1]
    
    def getState(self):
        return rd.randint(0, 1)
    
    def runStep(self):
        state = self.getState()  # S
        self.agent.legalActions = self.getLegalActions(state)  # give legal actions to the agent given the state
        action = self.agent.selectAction(state)  # action
        # print(state, action)
        state = self.getState()  # S+1
        self.agent.updateQValues(state, action, self.getState(), self.getReward(state, action))