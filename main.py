#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colorama import Fore, Back, Style
import time
import random
from enum import IntEnum
from typing import Any
import os
import copy as cp
import random as rd


class RLAgent:

    def __init__(self) -> None:
        self.q = {}
        self.epsilon = 1.0  # exploration
        self.discountEpsilon = 0.995
        self.gamma = 0.1  # discount factor
        self.eta = 0.01  # learning rate
        self.legalActions = []

    def getRandomPolicy(self, state):
        return rd.choice(self.getLegalActions(state))
    
    def getBestPolicy(self, state):
        bestAction = 0
        actions = self.getLegalActions(state)
        for a in actions:
            if self.q[state, a] > self.q[state, bestAction]:
                bestAction = a
        return bestAction
    
    def getBestPolicyReward(self, state):
        bestAction = 0
        actions = self.getLegalActions(state)
        for a in actions:
            value = 0
            skip = False
            if (state, a) in self.q.keys():
                value = self.q[state, a]
            if (state, bestAction) not in self.q.keys():
                skip = True
            if skip or (value) > self.q[state, bestAction]:
                bestAction = a
        return self.q[state, bestAction]
    
    def updateQValues(self, old_state, actionDone, state, reward):
        # print(self.q)
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


class TypeNode(IntEnum):
    START = 0
    HOSPITAL = 1
    VICTIM = 2
    NONE = 3



class Edge(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @staticmethod
    def nextCoords(x, y, orientation):
        if orientation == Edge.UP:
            return x, y - 1
        if orientation == Edge.RIGHT:
            return x + 1, y
        if orientation == Edge.DOWN:
            return x, y + 1
        if orientation == Edge.LEFT:
            return x - 1, y

Orientation = Edge



class Action(IntEnum):
    MOVE = 0
    LEFT = 1
    RIGHT = 2
    PICK = 3
    DROP = 4
    NONE = 5

    @staticmethod
    def orientationFromAction(orientation, action):
        if action in [Action.PICK, Action.DROP, Action.NONE]:
            return None
        
        if action == Action.MOVE:
            return orientation

        if action == Action.LEFT:
            return Orientation((int(orientation) - 1) % 4)

        if action == Action.RIGHT:
            return Orientation((int(orientation) + 1) % 4)



class Node:
    def __init__(self, typeNode, indexTypeNode, edgeOpen):
        self.typeNode = typeNode
        self.indexTypeNode = indexTypeNode
        self.edgeOpen = set(edgeOpen)

        self.pathLength = []
    
    def __str__(self):
        result = Back.BLACK

        if self.typeNode == TypeNode.HOSPITAL:
            result = Back.BLUE
        if self.typeNode == TypeNode.START:
            result = Back.GREEN
        if self.typeNode == TypeNode.VICTIM:
            result = Back.RED

        if self.edgeOpen == {Edge.UP, Edge.DOWN}:
            result += '┃'
        elif self.edgeOpen == {Edge.LEFT, Edge.RIGHT}:
            result += '━'

        elif self.edgeOpen == {Edge.RIGHT, Edge.DOWN}:
            result += '┏'
        elif self.edgeOpen == {Edge.LEFT, Edge.DOWN}:
            result += '┓'
        elif self.edgeOpen == {Edge.UP, Edge.RIGHT}:
            result += '┗'
        elif self.edgeOpen == {Edge.UP, Edge.LEFT}:
            result += '┛'

        elif self.edgeOpen == {Edge.UP, Edge.DOWN, Edge.RIGHT}:
            result += '┣'
        elif self.edgeOpen == {Edge.UP, Edge.DOWN, Edge.LEFT}:
            result += '┫'
        elif self.edgeOpen == {Edge.RIGHT, Edge.LEFT, Edge.UP}:
            result += '┻'
        elif self.edgeOpen == {Edge.RIGHT, Edge.LEFT, Edge.DOWN}:
            result += '┳'
        
        else:
            result += '•'
        
        return result



class Agent:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation
    
    def __str__(self):
        result = Back.BLACK

        if self.orientation == Orientation.UP:
            result += '▲'
        elif self.orientation == Orientation.RIGHT:
            result += '▶'
        elif self.orientation == Orientation.DOWN:
            result += '▼'
        elif self.orientation == Orientation.LEFT:
            result += '◀'
    
        else:
            result += '•'

        return result

    def __call__(self):
        return Action(random.randint(0, 2))
    


class Environment:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.nodeGrid = [[Node(TypeNode.NONE, -1, {}) for y in range(h)] for x in range(w)]
        self.agentList = []

    def __str__(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                agent = self.agentAt(x, y)
                result += str(agent) if agent else str(self.nodeGrid[x][y])
            result += "\n"
        return result
    
    def getPerception(self, agent):
        return {}

    def agentAt(self, x, y):
        for a in self.agentList:
            if a.x == x and a.y == y:
                return a
        return None

    def getLinks(self, x, y):
        links = []
        for possibleOrientation in self.nodeGrid[x][y].edgeOpen:
            links += [(Orientation.nextCoords(x, y, possibleOrientation))]
        return links

    def processAction(self, agent, agentAction):
        actionOrientation = Action.orientationFromAction(agent.orientation, agentAction)
        if actionOrientation in self.nodeGrid[agent.x][agent.y].edgeOpen:
            agent.x, agent.y = Orientation.nextCoords(agent.x, agent.y, actionOrientation)
            agent.orientation = actionOrientation
            
    def __call__(self):
        for agent in self.agentList:
            agentAction = agent()
            self.processAction(agent, agentAction)
    
    def addAgent(self, x, y, o):
        agent = Agent(x, y, o)
        agent.id = len(self.agentList)
        self.agentList += [agent]

    def simulate(self, action):
        pass

    def getNeihbourStates(self):
        actions = []
        for agent in self.agentList:
            actions.append(self.getPossibleMoves(agent))
        states = []
        for a in actions:
            pass

    def isInf(self, a, b, f):
        return f(a) <= f(b)
    
    def distPathLength(self, a):
        return a.pathLength

    def getPriority(self, q):
        index = None
        for i, e in enumerate(q):
            if index is None or self.isInf(e, q[index], self.distPathLength):
                index = i
        if index is None:
            return None
        e = q.pop(index)
        return e

    def processElement(self, e, queue, nodes, coordToIndex):
        # update the color and add neighbours to queue
        e.color = 2
        neighbours = self.getLinks(e.coord[0], e.coord[1])
        for n in neighbours:
            if nodes[coordToIndex[n]].color == 0:
                nodes[coordToIndex[n]].color = 1
                nodes[coordToIndex[n]].pathLength = e.pathLength + 1
                nodes[coordToIndex[n]].orientation = e.orientation
                nodes[coordToIndex[n]].state = self.simulate()
                queue.append(nodes[coordToIndex[n]])


    def dijkstra(self):
        # map each cel of the grid to the closest agent
        current = None
        queue = []
        nodes = []
        coordToIndex = dict()
        index = 0
        for y in range(self.h):
            for x in range(self.w):
                agent = self.agentAt(x, y)
                node = PathNode(x, y)
                if agent is not None:
                    node.agent = agent
                    node.color = 1
                    queue.append(node)
                nodes.append(node)
                coordToIndex[node.coord] = index
                index += 1


        current = self.getPriority(queue)
        while current is not None:
            self.processElement(current, queue, nodes, coordToIndex)
            current = self.getPriority(queue)

        for y in range(self.h):  # update nodes pathLength
            for x in range(self.w):
                self.nodeGrid[x][y].pathLength = nodes[coordToIndex[(x, y)]].pathLength



class PathNode:

    def __init__(self, x, y, orientation=-1, color=0) -> None:
        self.coord = (x, y)
        self.orientation = orientation
        self.color = color
        self.pathLength = 0
        self.state = None



environment = Environment(5, 5)
environment.nodeGrid[0][0] = Node(TypeNode.VICTIM, 1, {Edge.DOWN, Edge.RIGHT})
environment.nodeGrid[1][0] = Node(TypeNode.VICTIM, 2, {Edge.LEFT, Edge.RIGHT})
environment.nodeGrid[2][0] = Node(TypeNode.START, 1, {Edge.LEFT, Edge.DOWN, Edge.RIGHT})
environment.nodeGrid[3][0] = Node(TypeNode.VICTIM, 3, {Edge.LEFT, Edge.DOWN})
environment.nodeGrid[4][0] = Node(TypeNode.NONE, 0, {})

environment.nodeGrid[0][1] = Node(TypeNode.NONE, 0, {Edge.DOWN, Edge.UP})
environment.nodeGrid[1][1] = Node(TypeNode.NONE, 0, {})
environment.nodeGrid[2][1] = Node(TypeNode.VICTIM, 4, {Edge.UP, Edge.DOWN, Edge.RIGHT})
environment.nodeGrid[3][1] = Node(TypeNode.HOSPITAL, 1, {Edge.UP, Edge.DOWN, Edge.LEFT})
environment.nodeGrid[4][1] = Node(TypeNode.NONE, 0, {})

environment.nodeGrid[0][2] = Node(TypeNode.NONE, 0, {Edge.UP, Edge.DOWN, Edge.RIGHT})
environment.nodeGrid[1][2] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.RIGHT})
environment.nodeGrid[2][2] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.RIGHT, Edge.UP})
environment.nodeGrid[3][2] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.RIGHT, Edge.UP})
environment.nodeGrid[4][2] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.DOWN})

environment.nodeGrid[0][3] = Node(TypeNode.NONE, 0, {Edge.UP, Edge.DOWN})
environment.nodeGrid[1][3] = Node(TypeNode.NONE, 0, {})
environment.nodeGrid[2][3] = Node(TypeNode.HOSPITAL, 2, {Edge.RIGHT, Edge.DOWN})
environment.nodeGrid[3][3] = Node(TypeNode.START, 2, {Edge.LEFT, Edge.RIGHT, Edge.DOWN})
environment.nodeGrid[4][3] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.UP})

environment.nodeGrid[0][4] = Node(TypeNode.START, 3, {Edge.UP, Edge.RIGHT})
environment.nodeGrid[1][4] = Node(TypeNode.VICTIM, 5, {Edge.LEFT, Edge.RIGHT})
environment.nodeGrid[2][4] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.RIGHT, Edge.UP})
environment.nodeGrid[3][4] = Node(TypeNode.NONE, 0, {Edge.LEFT, Edge.UP})
environment.nodeGrid[4][4] = Node(TypeNode.NONE, 0, {})

environment.addAgent(0, 1, Orientation.DOWN)
environment.addAgent(1, 2, Orientation.DOWN)

print(environment)
env = TestEnv()
for _ in range(300):
    #environment()
    # environment.voronoi()
    # os.system('clear')
    #print(environment)
    env.runStep()
    time.sleep(0.1)
