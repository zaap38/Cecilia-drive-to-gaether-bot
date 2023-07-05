from __future__ import annotations
from typing import List, Tuple
from enum import IntEnum


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
        result = ''  # Back.BLACK

        # if self.typeNode == TypeNode.HOSPITAL:
        #     result = Back.BLUE
        # if self.typeNode == TypeNode.START:
        #     result = Back.GREEN
        # if self.typeNode == TypeNode.VICTIM:
        #     result = Back.RED

        if self.openOrientations == {Orientation.UP, Orientation.DOWN}:
            result += '┃'
        elif self.openOrientations == {Orientation.LEFT, Orientation.RIGHT}:
            result += '━'

        elif self.openOrientations == {Orientation.RIGHT, Orientation.DOWN}:
            result += '┏'
        elif self.openOrientations == {Orientation.LEFT, Orientation.DOWN}:
            result += '┓'
        elif self.openOrientations == {Orientation.UP, Orientation.RIGHT}:
            result += '┗'
        elif self.openOrientations == {Orientation.UP, Orientation.LEFT}:
            result += '┛'

        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.RIGHT}:
            result += '┣'
        elif self.openOrientations == {Orientation.UP, Orientation.DOWN, Orientation.LEFT}:
            result += '┫'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.UP}:
            result += '┻'
        elif self.openOrientations == {Orientation.RIGHT, Orientation.LEFT, Orientation.DOWN}:
            result += '┳'
        
        else:
            result += '•'

        if self.agentFlag.index != -1:
            result = str(self.agentFlag.index)
        
        return result


class Environment:
    def __init__(self, w: int=5, h: int=5):
        self.w = w
        self.h = h
        self.cellGrid = [[Cell(x, y) for y in range(h)] for x in range(w)]

    def getLegalActions(self, agentId):
        agentCell = self._getCellAgent(agentId)

        legalActions = []
        if agentCell.agentFlag.orientation.getLeft() in agentCell.openOrientations:
            legalActions += [Action.LEFT]
        if agentCell.agentFlag.orientation in agentCell.openOrientations:
            legalActions += [Action.MOVE]
        if agentCell.agentFlag.orientation.getRight() in agentCell.openOrientations:
            legalActions += [Action.RIGHT]

        return legalActions

    def setCell(self, x, y, agentIndex: int=-1, agentOrientation: Orientation=Orientation.UP, agentInventory: List[int]=[], hospitalIndex: int=-1, startIndex: int=-1, startOrientation: Orientation=Orientation.UP, victimIndex: int=-1, openOrientations: set[Orientation]={}):
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
            self.doLeft(agentId)
        if action == Action.MOVE:
            self.doMove(agentId)
        if action == Action.RIGHT:
            self.doRight(agentId)
        if action == Action.PICK:
            self.doPick(agentId)
        if action == Action.DROP:
            self.doDrop(agentId)
        if action == Action.NONE:
            self.doNone(agentId)

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

        if len(agentCell.agentFlag.inventory) == 0:
            return False
        
        agentCell.agentFlag.inventory = []
    
    def doNone(self, agentId):
        pass

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

    def __str__(self):
        result = ""
        for y in range(self.h):
            for x in range(self.w):
                result += str(self.cellGrid[x][y])
            result += "\n"
        return result
    

environment = Environment()
environment.setCell(0, 0, agentIndex=0, agentOrientation=Orientation.RIGHT, openOrientations={Orientation.DOWN, Orientation.RIGHT})
environment.setCell(1, 0, openOrientations={Orientation.LEFT, Orientation.RIGHT})
environment.setCell(2, 0, openOrientations={Orientation.LEFT, Orientation.DOWN, Orientation.RIGHT})
environment.setCell(3, 0, openOrientations={Orientation.LEFT, Orientation.DOWN})
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
environment.setCell(3, 3, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.DOWN})
environment.setCell(4, 3, openOrientations={Orientation.LEFT, Orientation.UP})

environment.setCell(0, 4, openOrientations={Orientation.UP, Orientation.RIGHT})
environment.setCell(1, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT})
environment.setCell(2, 4, openOrientations={Orientation.LEFT, Orientation.RIGHT, Orientation.UP})
environment.setCell(3, 4, openOrientations={Orientation.LEFT, Orientation.UP})
environment.setCell(4, 4, openOrientations={})

print(environment)
print(environment.getLegalActions(0))
environment.doAction(0, Action.MOVE)
print(environment)
print(environment.getLegalActions(0))
environment.doAction(0, Action.MOVE)
print(environment)
print(environment.getLegalActions(0))
environment.doAction(0, Action.MOVE)
print(environment)
print(environment.getLegalActions(0))
