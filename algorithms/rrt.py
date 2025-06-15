import random
import math
import matplotlib.pyplot as plt
import time
import sys

# Utility Functions
def create_node(x, y):
    return (x, y)

def distance(n1, n2):
    return math.hypot(math.floor(n1['x'] - n2['x']), math.floor(n1['y'] - n2['y']))

def distance(n1, n2):
    return math.hypot(n1['x'] - n2['x']),


def getRandomPoint(limit):
    return math.floor(random.uniform(0, limit))

def getRandomPosition(x_limit, y_limit):
    x = getRandomPoint(x_limit)
    y = getRandomPoint(y_limit)
    return (x, y)

def isObstacle(point, obstacles, r=1):
    return point in obstacles

def nearest_node(tree, new_node):
    return min(tree, key=lambda n: distance(n, new_node))

def findPath (parents, start, end):
    path = []
    current = end
    while current != start:
        path.append(current)
        if current not in parents:
            return path
        current = parents[current]
    path.append(start)
    return path[::-1]

def convertTreeToUniqueList (tree):
    obj = {}
    for node in tree:
        obj[f"{node[0]}:{node[1]}"] = None
    return obj

def nodeIsValid (parents, node, obstacles, xLimit, yLimit):
    if node in obstacles:
        return False
    if node[0] > xLimit or node[1] > yLimit:
        return False
    if node in parents:
        return False
    return True

def sendData (socketInformation, parents, startNode, goalNode):

    if socketInformation == None:
        return

    if 'io' not in socketInformation:
        return

    path = findPath(parents, startNode, goalNode) if goalNode else []
    path = convertTreeToUniqueList(path)

    parentStringEdition = convertTreeToUniqueList(parents)

    if 'sleepDuration' in socketInformation:
        time.sleep(socketInformation['sleepDuration'])

    socketInformation['io'].emit('message', { 'meta':{'algorithm':'RRT',  'visitSize':len(parents) }, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'path':path, 'barriers':socketInformation.get('stringBarriers'), 'visited':parentStringEdition })

    # socketInformation['io'].emit('message', {
    #     'path':path,
    #     'visited': parentStringEdition,
    #     'gridSize': socketInformation.get('gridSize'),
    #     'barriers': socketInformation.get('stringBarriers'),
    #     'meta':
    #     {   'algorithm':'RRT',
    #         'visitSize':len(parents),
    #         'gridSize':socketInformation.get('gridSize'),
    #         'id':socketInformation.get('id'),
    #         'path':path,
    #         'barriers':socketInformation.get('stringBarriers'),
    #         'visited': parentStringEdition
    #     }
    # })

def distanceApart (cordA, cordB):
    return abs(cordA[0]-cordB[0]) + abs(cordA[1]-cordB[1])

def findNearestParent (parents, startNode, node):
    maxDistance = distanceApart(startNode, node)
    closestNode = startNode

    for parent in parents:
        distance = distanceApart(parent, node)
        if distance < maxDistance:
            closestNode = parent
            maxDistance = distance

    return closestNode

def rrt (parentBlock, start, end, obstacles, gridSize, maxIterations, socketInformation=None):
    index = 0
    while index <= maxIterations:
        index+=1
        newRandomPosition = getRandomPosition(gridSize, gridSize)
        parentNode = findNearestParent(parentBlock, start, newRandomPosition)
        valid = nodeIsValid(parentBlock, newRandomPosition, obstacles, gridSize, gridSize)
        if not valid:
            continue
        parentBlock[newRandomPosition] = parentNode
        sendData(socketInformation, parentBlock, start, newRandomPosition)
        if newRandomPosition == end:
            break

    return {}, end


def rrtRunner (start, end, obstacles, gridSize, maxIterations, socketInformation=None):
    parentBlock = {}
    rrt(parentBlock, start, end, obstacles, gridSize, maxIterations, socketInformation)
    path = findPath (parentBlock, start, end)
    return path, parentBlock
