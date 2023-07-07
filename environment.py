from __future__ import annotations
from colorama import Fore, Back
from enum import IntEnum
from typing import List
import copy as cp
import time

from rlagent import RLAgent

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

    def __repr__(self):
        result = '(' + str(self.x) + ', ' + str(self.y) + ', '

        result += 'A' + str(self.agentFlag.index) + str(self.agentFlag.orientation) + ''.join(sorted([str(x) for x in self.agentFlag.inventory])) + ', '
        result += 'H' + str(self.hospitalFlag.index) + ', '
        result += 'V' + str(self.victimFlag.index) + ')'

        return result

    def __str__(self):
        background = Back.BLACK
        foreground = Fore.WHITE

        if self.hospitalFlag.index != -1:
            background = Back.BLUE

        if self.victimFlag.index != -1:
            background = Back.RED
        
        if len(self.agentFlag.inventory) == 1:
            foreground = Fore.LIGHTRED_EX
                
        if len(self.agentFlag.inventory) == 2:
            foreground = Fore.RED

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
            if self.agentFlag.orientation == Orientation.UP:
                result = '▲'
            elif self.agentFlag.orientation == Orientation.RIGHT:
                result = '▶'
            elif self.agentFlag.orientation == Orientation.DOWN:
                result = '▼'
            elif self.agentFlag.orientation == Orientation.LEFT:
                result = '◀'
        
        return background + foreground + result + Back.BLACK + Fore.WHITE


class Environment:
    def __init__(self, w: int=5, h: int=5):
        self.w = w
        self.h = h
        self.cellGrid = [[Cell(x, y) for y in range(h)] for x in range(w)]
        self.saved = 0

    def runStep(self, agent):
        state = repr(self)
        action = agent.selectAction(state, self.getLegalActions(agent.id))
        reward = self.doAction(agent.id, action)
        
        old_state = cp.deepcopy(state)
        state = repr(self)
        final = self.isFinal()
        agent.updateQValues(old_state, action, state, reward, final)

        if final: self.reset()

    def getLegalActions(self, agentId):
        agentCell = self._getCellAgent(agentId)

        legalActions = []
        if agentCell.agentFlag.orientation.getLeft() in agentCell.openOrientations:
            legalActions += [Action.LEFT]
        if agentCell.agentFlag.orientation in agentCell.openOrientations:
            legalActions += [Action.MOVE]
        if agentCell.agentFlag.orientation.getRight() in agentCell.openOrientations:
            legalActions += [Action.RIGHT]
        if agentCell.victimFlag.index != -1 and len(agentCell.agentFlag.inventory) < 2:
            legalActions += [Action.PICK]
        if agentCell.hospitalFlag.index != -1 and len(agentCell.agentFlag.inventory) > 0:
            legalActions += [Action.DROP]

        return legalActions

    def setCell(self, x, y, agentIndex: int=-1, agentOrientation: Orientation=Orientation.UP,
                agentInventory=[], hospitalIndex: int=-1, startIndex: int=-1,
                startOrientation: Orientation=Orientation.UP, victimIndex: int=-1, openOrientations: set[Orientation]={}):
        self.cellGrid[x][y].agentFlag.index = agentIndex
        self.cellGrid[x][y].agentFlag.orientation = agentOrientation
        self.cellGrid[x][y].agentFlag.inventory = [] if len(agentInventory) == 0 else agentInventory

        self.cellGrid[x][y].hospitalFlag.index = hospitalIndex

        self.cellGrid[x][y].startFlag.index = startIndex
        self.cellGrid[x][y].startFlag.orientation = startOrientation

        self.cellGrid[x][y].victimFlag.index = victimIndex

        self.cellGrid[x][y].openOrientations = {} if len(openOrientations) == 0 else openOrientations

    def doAction(self, agentId, action):
        if action == Action.LEFT:
            status, reward = self.doLeft(agentId)
        if action == Action.MOVE:
            status, reward = self.doMove(agentId)
        if action == Action.RIGHT:
            status, reward = self.doRight(agentId)
        if action == Action.PICK:
            status, reward = self.doPick(agentId)
        if action == Action.DROP:
            status, reward = self.doDrop(agentId)
        if action == Action.NONE:
            status, reward = self.doNone(agentId)

        if not status:
            reward -= 10
        reward -= 1

        return reward

    def doLeft(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation.getLeft()
        return self._moveOrientation(nextOrientation, agentCell), 0

    def doMove(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation
        return self._moveOrientation(nextOrientation, agentCell), 0
    
    def doRight(self, agentId):
        agentCell = self._getCellAgent(agentId)

        nextOrientation = agentCell.agentFlag.orientation.getRight()
        return self._moveOrientation(nextOrientation, agentCell), 0
    
    def doPick(self, agentId):
        agentCell = self._getCellAgent(agentId)

        if agentCell.victimFlag.index == -1:
            return False, 0
        
        agentCell.agentFlag.inventory += [agentCell.victimFlag.index]
        agentCell.victimFlag.index = -1

        return True, 50

    def doDrop(self, agentId):
        agentCell = self._getCellAgent(agentId)
        nbVictim = len(agentCell.agentFlag.inventory)

        self.saved += nbVictim

        if nbVictim == 0:
            return False, 0
        
        agentCell.agentFlag.inventory = []
        return True, nbVictim*100
    
    def doNone(self, agentId):
        return True, 0
    
    def isFinal(self):
        for x in range(self.w):
            for y in range(self.h):
                if self.cellGrid[x][y].victimFlag.index != -1 or len(self.cellGrid[x][y].agentFlag.inventory) != 0:
                    return False

        return True

    def reset(self):
        self.setCell(0, 0, agentIndex=0, agentOrientation=Orientation.RIGHT, openOrientations={Orientation.DOWN, Orientation.RIGHT}, victimIndex=0)
        self.setCell(1, 0, openOrientations={Orientation.LEFT, Orientation.RIGHT})
        self.setCell(2, 0, openOrientations={Orientation.LEFT, Orientation.DOWN, Orientation.RIGHT})
        self.setCell(3, 0, openOrientations={Orientation.LEFT, Orientation.DOWN}, hospitalIndex=1)
        self.setCell(4, 0, openOrientations={})

        self.setCell(0, 1, openOrientations={Orientation.DOWN, Orientation.UP})
        self.setCell(1, 1, openOrientations={})
        self.setCell(2, 1, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.RIGHT})
        self.setCell(3, 1, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.LEFT})
        self.setCell(4, 1, openOrientations={})

        self.setCell(0, 2, openOrientations={Orientation.UP, Orientation.DOWN, Orientation.RIGHT})
        self.setCell(1, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT})
        self.setCell(2, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
        self.setCell(3, 2, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
        self.setCell(4, 2, openOrientations={Orientation.LEFT, Orientation.DOWN})

        self.setCell(0, 3, openOrientations={Orientation.UP, Orientation.DOWN})
        self.setCell(1, 3, openOrientations={})
        self.setCell(2, 3, openOrientations={Orientation.RIGHT, Orientation.DOWN})
        self.setCell(3, 3, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.DOWN})
        self.setCell(4, 3, openOrientations={Orientation.LEFT, Orientation.UP})

        self.setCell(0, 4, openOrientations={Orientation.UP, Orientation.RIGHT})
        self.setCell(1, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT})
        self.setCell(2, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
        self.setCell(3, 4, openOrientations={Orientation.LEFT, Orientation.UP})
        self.setCell(4, 4, openOrientations={})

    def _getCellAgent(self, agentId):
        for x in range(self.w):
            for y in range(self.h):
                if self.cellGrid[x][y].agentFlag.index == agentId:
                    return self.cellGrid[x][y]
    
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

    def __repr__(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                result += repr(self.cellGrid[x][y]) + '\n'
        return result

    def __str__(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                result += str(self.cellGrid[x][y])
            result += "\n"
        return result
    




environment = Environment()
environment.reset()

agent = RLAgent(environment)
for step in range(1000000):

    if step <= 150000:
        if step % 10000 == 0:
            print(step)
    else:
        time.sleep(0.3)
        print("STEP:", step, "SAVED:", environment.saved, "VISITED:", str(len(agent.q)))
        print(environment)

    environment.runStep(agent)
