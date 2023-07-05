#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from enum import IntEnum
from typing import Any
import os



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
    
    def __str__(self):
        if self.edgeOpen == {Edge.UP, Edge.DOWN}:
            return '┃'
        elif self.edgeOpen == {Edge.LEFT, Edge.RIGHT}:
            return '━'

        elif self.edgeOpen == {Edge.RIGHT, Edge.DOWN}:
            return '┏'
        elif self.edgeOpen == {Edge.LEFT, Edge.DOWN}:
            return '┓'
        elif self.edgeOpen == {Edge.UP, Edge.RIGHT}:
            return '┗'
        elif self.edgeOpen == {Edge.UP, Edge.LEFT}:
            return '┛'

        elif self.edgeOpen == {Edge.UP, Edge.DOWN, Edge.RIGHT}:
            return '┣'
        elif self.edgeOpen == {Edge.UP, Edge.DOWN, Edge.LEFT}:
            return '┫'
        elif self.edgeOpen == {Edge.RIGHT, Edge.LEFT, Edge.UP}:
            return '┻'
        elif self.edgeOpen == {Edge.RIGHT, Edge.LEFT, Edge.DOWN}:
            return '┳'
        
        else:
            return '•'



class Agent:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation
    
    def __str__(self):
        if self.orientation == Orientation.UP:
            return '▲'
        elif self.orientation == Orientation.RIGHT:
            return '▶'
        elif self.orientation == Orientation.DOWN:
            return '▼'
        elif self.orientation == Orientation.LEFT:
            return '◀'
    
        else:
            return '•'

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
        for possibleOrientation in self.nodeGrid[x][y]:
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

    def isInf(self, a, b, f):
        return f(a) <= f(b)

    def getPriority(self, q):
        index = None
        for i, e in enumerate(q):
            if index is None or self.isInf(e, q[index]):
                index = i
        if index is None:
            return None
        e = q.pop(index)
        return e, q

    def processElement(self, e, queue, nodes):
        # update the color and add neighbours to queue
        e.color = 2
        neighbours = self.getNeighboursByCoord(e)
        for n in neighbours:
            if True:
                queue.append(n)


    def voronoi(self):
        # map each cel of the grid to the closest agent
        current = None
        queue = []
        nodes = []
        for y in range(self.h):
            for x in range(self.w):
                agent = self.agentAt(x, y)
                if agent is not None:
                    queue.append(PathNode(x, y, agent.id, 1))
                else:
                    nodes.append(PathNode(x, y))

        current, queue = self.getPriority(queue)
        while current is not None:
            self.processElement(current)
            current, queue = self.getPriority(queue)


class PathNode:

    def __init__(self, x, y, agent=-1, color=0) -> None:
        self.coord = (x, y)
        self.agent = agent
        self.color = color



environment = Environment(4, 5)
environment.nodeGrid[0][0] = Node(TypeNode.VICTIM, 1, {Edge.RIGHT, Edge.DOWN})
environment.nodeGrid[1][0] = Node(TypeNode.NONE, 1, {Edge.LEFT, Edge.RIGHT})
environment.nodeGrid[2][0] = Node(TypeNode.NONE, 1, {Edge.LEFT, Edge.DOWN})
environment.nodeGrid[0][1] = Node(TypeNode.NONE, 1, {Edge.UP, Edge.DOWN})
environment.nodeGrid[1][1] = Node(TypeNode.NONE, 1, {})
environment.nodeGrid[2][1] = Node(TypeNode.NONE, 1, {Edge.UP, Edge.DOWN})
environment.nodeGrid[0][2] = Node(TypeNode.NONE, 1, {Edge.RIGHT, Edge.UP})
environment.nodeGrid[1][2] = Node(TypeNode.NONE, 1, {Edge.RIGHT, Edge.LEFT})
environment.nodeGrid[2][2] = Node(TypeNode.NONE, 1, {Edge.UP, Edge.LEFT})
environment.addAgent(0, 1, Orientation.DOWN)

print(environment)
for _ in range(300):
    environment()
    os.system('clear')
    print(environment)
    time.sleep(0.1)

