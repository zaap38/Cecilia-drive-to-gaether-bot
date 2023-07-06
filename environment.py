from __future__ import annotations
from typing import List, Tuple
from enum import IntEnum
from rlagent import RLAgent
import copy as cp
import time
import os
from colorama import Fore, Back, Style
import random as rd

saved = 0

class Action(IntEnum):
    MOVE = 0
    LEFT = 1
    RIGHT = 2
    PICK = 3
    DROP = 4
    NONE = 5


class Orientation(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def getOffset(self) -> tuple[int, int]:
        if self == Orientation.UP:
            return 0, -1
        if self == Orientation.RIGHT:
            return +1, 0
        if self == Orientation.DOWN:
            return 0, +1
        if self == Orientation.LEFT:
            return -1, 0

    def getLeft(self) -> Orientation:
        return Orientation((int(self) - 1)%4)

    def getRight(self) -> Orientation:
        return Orientation((int(self) + 1)%4)


class AgentFlag:
    def __init__(self, index: int=-1, orientation: Orientation=Orientation.UP, inventory: List[int]=[]):
        self.index = index
        self.orientation = orientation
        self.inventory = inventory


class HospitalFlag:
    def __init__(self, index: int=-1):
        self.index = index


class StartFlag:
    def __init__(self, index: int=-1, orientation: Orientation=Orientation.UP):
        self.index = index
        self.orientation = orientation


class VictimFlag:
    def __init__(self, index: int=-1):
        self.index = index


class Cell:
    def __init__(self, x, y, agentIndex: int=-1, agentOrientation: Orientation=Orientation.UP, agentInventory: List[int]=[], hospitalIndex: int=-1, startIndex: int=-1, startOrientation: Orientation=Orientation.UP, victimIndex: int=-1, openOrientations: set[Orientation]={}):
        self.x = x
        self.y = y
        self.agentFlag = AgentFlag(agentIndex, agentOrientation, agentInventory)
        self.hospitalFlag = HospitalFlag(hospitalIndex)
        self.startFlag = StartFlag(startIndex, startOrientation)
        self.victimFlag = VictimFlag(victimIndex)
        self.openOrientations = openOrientations

    def __str__(self):
        # result = ''  # Back.BLACK

        # if self.typeNode == TypeNode.HOSPITAL:
        #     result = Back.BLUE
        # if self.typeNode == TypeNode.START:
        #     result = Back.GREEN
        # if self.typeNode == TypeNode.VICTIM:
        #     result = Back.RED

        bg = Back.BLACK
        fg = Fore.WHITE

        if self.hospitalFlag.index > 0:
            bg = Back.BLUE
        if self.victimFlag.index > 0:
            bg = Back.RED

        if self.openOrientations == {Orientation.UP, Orientation.DOWN}:
            result = '┃'
        elif self.openOrientations == {Orientation.LEFT, Orientation.RIGHT}:
            result = '━'

        elif self.openOrientations == {Orientation.RIGHT, Orientation.DOWN}:
            result = '┏'
        elif self.openOrientations == {Orientation.LEFT, Orientation.DOWN}:
            result = '┓'
        elif self.openOrientations == {Orientation.UP, Orientation.RIGHT}:
            result = '┗'
        elif self.openOrientations == {Orientation.UP, Orientation.LEFT}:
            result = '┛'

        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.RIGHT}:
            result = '┣'
        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.LEFT}:
            result = '┫'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.UP}:
            result = '┻'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.DOWN}:
            result = '┳'
        
        else:
            result = '•'

        if self.agentFlag.index != -1:
            #result = str(self.agentFlag.index)
            if self.agentFlag.orientation == Orientation.UP:
                result = '▲'
            elif self.agentFlag.orientation == Orientation.RIGHT:
                result = '▶'
            elif self.agentFlag.orientation == Orientation.DOWN:
                result = '▼'
            elif self.agentFlag.orientation == Orientation.LEFT:
                result = '◀'
            if len(self.agentFlag.inventory) > 0:
                fg = Fore.RED
            
        
        return bg + fg + result + Back.BLACK
    
    def getStrNoColor(self):

        if self.openOrientations == {Orientation.UP, Orientation.DOWN}:
            result = '┃'
        elif self.openOrientations == {Orientation.LEFT, Orientation.RIGHT}:
            result = '━'

        elif self.openOrientations == {Orientation.RIGHT, Orientation.DOWN}:
            result = '┏'
        elif self.openOrientations == {Orientation.LEFT, Orientation.DOWN}:
            result = '┓'
        elif self.openOrientations == {Orientation.UP, Orientation.RIGHT}:
            result = '┗'
        elif self.openOrientations == {Orientation.UP, Orientation.LEFT}:
            result = '┛'

        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.RIGHT}:
            result = '┣'
        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.LEFT}:
            result = '┫'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.UP}:
            result = '┻'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.DOWN}:
            result = '┳'
        
        else:
            result = '•'

        if self.agentFlag.index != -1:
            #result = str(self.agentFlag.index)
            if self.agentFlag.orientation == Orientation.UP:
                result = '▲'
            elif self.agentFlag.orientation == Orientation.RIGHT:
                result = '▶'
            elif self.agentFlag.orientation == Orientation.DOWN:
                result = '▼'
            elif self.agentFlag.orientation == Orientation.LEFT:
                result = '◀'

        if self.victimFlag.index != -1:
            result = 'V'
            
        
        return result


class Environment:
    def __init__(self, w: int=5, h: int=5):
        self.w = w
        self.h = h
        self.cellGrid = [[Cell(x, y) for y in range(h)] for x in range(w)]
        self.saved = 0
        self.currentSaved = 4

    def getState(self, agent):
        # hash current state
        hashRaw = self.getStrNoColor()
        agentCell = self._getCellAgent(agent.id)
        hashRaw += str(len(agentCell.agentFlag.inventory))
        return hashRaw#hash(hashRaw)

    def updateState(self, agent, action):
        # process action and return reward
        # illegal action -> -10
        # reach victim with space -> +5
        # drop victim to hospital -> +5 per victim
        # default (time) -> -1
        # TODO: add an action "wait[DIR]" which converts to DIR for the server but returns default reward if NOP
        status = self.doAction(agent.id, action)
        reward = -10
        if status:
            if action in [Action.LEFT, Action.RIGHT, Action.MOVE]:
                reward = -1
                #if action == Action.MOVE:  # test
                #    reward = 1
            if action == Action.DROP:
                reward = 100  # times victim dropped count
            if action == Action.PICK:
                reward = 50
            if action == Action.NONE:
                reward = -1
        return reward

    def runStep(self, agent, forceExplore=False, idiotDuVillage=False):
        state = self.getState(agent)
        agent.legalActions = self.getLegalActions(agent.id)
        action = agent.selectAction(state, forceExplore)
        if idiotDuVillage:  # idiot -------------
            agentCell = self._getCellAgent(agent.id)
            if agentCell.victimFlag.index != -1:
                if len(agentCell.agentFlag.inventory) < 2:
                    action = Action.PICK
            if agentCell.hospitalFlag.index != -1:
                if len(agentCell.agentFlag.inventory) > 0:
                    action = Action.DROP # ------
        reward = self.updateState(agent, action)
        agent.lastReward = reward
        old_state = cp.deepcopy(state)
        state = self.getState(agent)
        agent.legalActions = self.getLegalActions(agent.id)
        final = self.currentSaved == 5
        agent.updateQValues(old_state, action, state, reward, final)

    def getLegalActions(self, agentId):
        agentCell = self._getCellAgent(agentId)

        legalActions = []
        if agentCell.agentFlag.orientation.getLeft() in agentCell.openOrientations and \
                self.simulateMove(agentCell, agentCell.agentFlag.orientation.getLeft()).agentFlag.index == -1:
            legalActions += [Action.LEFT]
        if agentCell.agentFlag.orientation in agentCell.openOrientations and \
                self.simulateMove(agentCell, agentCell.agentFlag.orientation).agentFlag.index == -1:
            legalActions += [Action.MOVE]
        if agentCell.agentFlag.orientation.getRight() in agentCell.openOrientations and \
                self.simulateMove(agentCell, agentCell.agentFlag.orientation.getRight()).agentFlag.index == -1:
            legalActions += [Action.RIGHT]
        if agentCell.victimFlag.index != -1 and len(agentCell.agentFlag.inventory) < 2:
            legalActions += [Action.PICK]
        if agentCell.hospitalFlag.index != -1 and len(agentCell.agentFlag.inventory) > 0:
            legalActions += [Action.DROP]

        return legalActions

    def setCell(self, x, y, agentIndex: int=-1, agentOrientation: Orientation=Orientation.UP,
                agentInventory: List[int]=[], hospitalIndex: int=-1, startIndex: int=-1,
                startOrientation: Orientation=Orientation.UP, victimIndex: int=-1, openOrientations: set[Orientation]={}):
        self.cellGrid[x][y].agentFlag.index = agentIndex
        self.cellGrid[x][y].agentFlag.orientation = agentOrientation
        self.cellGrid[x][y].agentFlag.inventory = agentInventory

        self.cellGrid[x][y].hospitalFlag.index = hospitalIndex

        self.cellGrid[x][y].startFlag.index = startIndex
        self.cellGrid[x][y].startFlag.orientation = startOrientation

        self.cellGrid[x][y].victimFlag.index = victimIndex

        self.cellGrid[x][y].openOrientations = openOrientations

    def doAction(self, agentId, action):
        if action == Action.LEFT:
            status = self.doLeft(agentId)
        if action == Action.MOVE:
            status = self.doMove(agentId)
        if action == Action.RIGHT:
            status = self.doRight(agentId)
        if action == Action.PICK:
            status = self.doPick(agentId)
        if action == Action.DROP:
            status = self.doDrop(agentId)
        if action == Action.NONE:
            status = self.doNone(agentId)
        return status

    def doLeft(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation.getLeft()
        return self._moveOrientation(nextOrientation, agentCell)

    def doMove(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation
        return self._moveOrientation(nextOrientation, agentCell)
    
    def doRight(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation.getRight()
        return self._moveOrientation(nextOrientation, agentCell)
    
    def doPick(self, agentId):
        agentCell = self._getCellAgent(agentId)

        if agentCell.victimFlag.index == -1:
            return False
        
        agentCell.agentFlag.inventory += [agentCell.victimFlag.index]
        agentCell.victimFlag.index = -1

        return True

    def doDrop(self, agentId):
        agentCell = self._getCellAgent(agentId)
        # test
        #x = rd.randint(0, self.w - 1)
        #y = rd.randint(0, self.h - 1)
        self.saved += len(agentCell.agentFlag.inventory)
        self.currentSaved += len(agentCell.agentFlag.inventory)
        """while True:
            x = rd.randint(0, self.w - 1)
            y = rd.randint(0, self.h - 1)
            x = 4
            y = 3
            if len(self.cellGrid[x][y].openOrientations) > 0:
                self.cellGrid[x][y].victimFlag.index = rd.randint(0, 10)
                return True"""
        if self.currentSaved == 5:
            self.currentSaved = 0
            self.cellGrid[0][0].victimFlag.index = 1
            self.cellGrid[1][0].victimFlag.index = 2
            self.cellGrid[3][0].victimFlag.index = 3
            self.cellGrid[2][1].victimFlag.index = 4
            self.cellGrid[1][4].victimFlag.index = 5


        if len(agentCell.agentFlag.inventory) == 0:
            return False
        
        agentCell.agentFlag.inventory = []
        return True
        # return False
    
    def doNone(self, agentId):
        pass

    def _getCellAgent(self, agentId):
        # print("vvvvvvvvvvvvvvvvvvvvvv")
        for x in range(self.w):
            for y in range(self.h):
                # print(self.cellGrid[x][y].agentFlag.index, "---", agentId)
                if self.cellGrid[x][y].agentFlag.index == agentId:
                    return self.cellGrid[x][y]
    
    def simulateMove(self, cell, orientation):
        if orientation not in cell.openOrientations:
            return None
        deltaX, deltaY = orientation.getOffset()
        return self.cellGrid[cell.x + deltaX][cell.y + deltaY]

    def _moveOrientation(self, orientation, cell):
        if orientation not in cell.openOrientations:
            return False

        deltaX, deltaY = orientation.getOffset()
        newCell = self.cellGrid[cell.x + deltaX][cell.y + deltaY]

        newCell.agentFlag.index = cell.agentFlag.index
        newCell.agentFlag.orientation = orientation
        newCell.agentFlag.inventory = cell.agentFlag.inventory

        cell.agentFlag.index = -1
        cell.agentFlag.orientation = Orientation.UP
        cell.agentFlag.inventory = []

        return True

    def __str__(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                result += str(self.cellGrid[x][y])
            result += "\n"
        return result
    
    def getStrNoColor(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                result += self.cellGrid[x][y].getStrNoColor()
            result += "\n"
        return result
    

agent = RLAgent(0)
walker = RLAgent(1)

environment = Environment()
environment.setCell(0, 0, openOrientations={Orientation.DOWN, Orientation.RIGHT})
environment.setCell(1, 0, openOrientations={Orientation.LEFT, Orientation.RIGHT})
environment.setCell(2, 0, agentIndex=agent.id, agentOrientation=Orientation.RIGHT, openOrientations={Orientation.LEFT, Orientation.DOWN, Orientation.RIGHT})
environment.setCell(3, 0, openOrientations={Orientation.LEFT, Orientation.DOWN}, hospitalIndex=1)
environment.setCell(4, 0, openOrientations={})

environment.setCell(0, 1, openOrientations={Orientation.DOWN, Orientation.UP})
environment.setCell(1, 1, openOrientations={})
environment.setCell(2, 1, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.RIGHT})
environment.setCell(3, 1, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.LEFT})
environment.setCell(4, 1, openOrientations={})

environment.setCell(0, 2, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.RIGHT})
environment.setCell(1, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT})
environment.setCell(2, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
environment.setCell(3, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
environment.setCell(4, 2, openOrientations={Orientation.LEFT, Orientation.DOWN})

environment.setCell(0, 3, openOrientations={Orientation.UP, Orientation.DOWN})
environment.setCell(1, 3, openOrientations={})
environment.setCell(2, 3, openOrientations={Orientation.RIGHT, Orientation.DOWN})
environment.setCell(3, 3, agentIndex=walker.id, agentOrientation=Orientation.RIGHT, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.DOWN})
environment.setCell(4, 3, openOrientations={Orientation.LEFT, Orientation.UP}, victimIndex=1)

environment.setCell(0, 4, openOrientations={Orientation.UP, Orientation.RIGHT})
environment.setCell(1, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT})
environment.setCell(2, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
environment.setCell(3, 4, openOrientations={Orientation.LEFT, Orientation.UP})
environment.setCell(4, 4, openOrientations={})

for step in range(1000000):
    # os.system('cls')
    forceExplore = False
    if step % 10000 == 0:
        print(step)
    if step > 0*150000:
        forceExplore = False
        time.sleep(0.3)
        print("STEP:", step, "SAVED:", environment.saved, "VISITED:", str(len(agent.q)))
        print(environment)
        print(round(agent.epsilon, 2), agent.lastReward, agent.lastAction, agent.getLegalActionRewards(environment.getState(agent)))
    environment.runStep(agent, forceExplore)
    environment.runStep(walker, True, True)

