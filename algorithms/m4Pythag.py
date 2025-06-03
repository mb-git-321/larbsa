import time
import math
# import rospy

"""
    MG5 can find a path between two nodes, with heuristic, with the magnetism enabled 
    This version is uses pythagoras instead of manhattan distance
"""

queue = ([], [])
obstacles = {}
traces = ({}, {})
reserves = ([], [])

def inBucket (cords, visited):
    return cords in visited

def filterOptions(cords, visited, obstacles):
    if inBucket(cords, visited):
        return False
    if inBucket(cords, obstacles):
        return False
    return True

def keysVersion (arr, appen=False):
    obj = {} if not appen else []
    for x in arr:
        if appen:
            obj.append(f'{x[0]}:{x[1]}')
        else:
            obj[f'{x[0]}:{x[1]}']=None
    return obj

def extractPath (end, nodes, reverse=True):
    currentlyAt = end
    path = [end]
    while currentlyAt in nodes and nodes[currentlyAt] != None:
        path.append(nodes[currentlyAt])
        currentlyAt = nodes[currentlyAt]

    return path[::-1] if reverse else path

def extractPathShorter (end, nodes, reverse=True):
    currentlyAt = end
    path = [end]
    index = 0
    while currentlyAt in nodes and nodes[currentlyAt] != None:
        size = len(path)
        if size > 2:
            curr = nodes[currentlyAt]
            rightAngle = path[size - 1]
            hasBlockedNeighbour = False
            thoughOptions = [
                (rightAngle[0]-1, rightAngle[1]-1),  
                (rightAngle[0]-1, rightAngle[1]+1),  
                (rightAngle[0]+1, rightAngle[1]+1),  
                (rightAngle[0]+1, rightAngle[1]-1),  
            ]

            for opt in thoughOptions:
                if opt in obstacles:
                    hasBlockedNeighbour = True
                    break
            if not hasBlockedNeighbour:
                path[size - 1] = curr
            else:
                path.append(curr)
            
            currentlyAt = nodes[currentlyAt]
            continue

        path.append(nodes[currentlyAt])
        # if 

        currentlyAt = nodes[currentlyAt]
        index+=1
    return path[::-1] if reverse else path    

# def runSingleIteration (currentInfo, queue, reserves, visitedTrace, visited, vistedNext, end, obstacles):
def runSingleIteration (currentInfo, queue, reserves, visitedTrace, vistedNext, end, obstacles):
    currentInfo['value'] = queue.pop(0) 
    current = currentInfo['value']
    thoughOptions = [
      (current[0]-1, current[1]),  # top
      (current[0], current[1]+1),  # right
      (current[0]+1, current[1]),  # bottom
      (current[0], current[1]-1),  # left
    ]
    
    options = []
    for opt in thoughOptions:
        include = filterOptions(opt, visitedTrace, obstacles)
        if include:
            options.append(opt)

    if not len(options) and len(reserves):
        # this is when we know we have rerouted since we are no longer taking the best option
        (parent, nextRes) = reserves.pop(0)
        visitedTrace[nextRes] = parent
        queue.append(nextRes)
        if nextRes in vistedNext:
            return nextRes
        return 1
    if not len(options) and len(queue):
        return 2        
    elif not len(options):
        # print('No path possible!')
        return -1   

    bestFitness = float('inf')
    bestCord = None

    for opt in options:
        fitness = math.sqrt ( math.pow(opt[0] - end[0], 2) + math.pow(opt[1] - end[1], 2) ) 
        if fitness < bestFitness:
            bestFitness = fitness
            bestCord = opt

    visitedTrace[bestCord] = current
    if bestCord in vistedNext:
        return bestCord
    queue.append(bestCord)

    for opt in options:
        if opt != bestCord:
            reserves.append((current, opt))    

    return True
def distanceApart (cordA, cordB):
    return abs(cordA[0]-cordB[0]) + abs(cordA[1]-cordB[1])

def heuristic(start, end, barriers, maxIterations=1000): #function for something else
    global obstacles
    obstacles = barriers
    queue = ([start], [end])
    # visited = ([start], [end])
    traces = ({start:None}, {end:None})
    reserves = ([], [])
    currents = [{'value':start}, {'value':end}]
    index = 0
    # add extra condition where visits overlay
    mergePoint = None
    restarts = 0
    while maxIterations >= 0 and len(queue[0]) and len(queue[1]) and distanceApart(currents[0]['value'], currents[1]['value']) > 1:
        try:
            nextIndex = (index+1) % 2
            # status = runSingleIteration (currents[index], queue[index], reserves[index], traces[index], visited[index], visited[nextIndex], currents[nextIndex]['value'], obstacles)
            status = runSingleIteration (currents[index], queue[index], reserves[index], traces[index], traces[nextIndex], currents[nextIndex]['value'], obstacles)
            if status == 1:
                restarts+=1
            if status == -1:
                return ([], [], "")
            if type(status) == tuple:
                mergePoint = status
                break

            index = nextIndex
            maxIterations -= 1
        except:
            return ([], [], "")

    if maxIterations <= 0:
        return ([], [], "PASSED-MAX-ITERATIONS")

    if mergePoint != None:
        p1 = extractPath(mergePoint, traces[0])
        p2 = extractPath(mergePoint, traces[1], False)
        # p2.pop(0) # deals with overlap
        path = p1 + p2[1:] 

        return (path, list(traces[0])+list(traces[1])+reserves[0]+reserves[1], f"MERGEPOINT R:{restarts}")

    return (extractPath(currents[0]['value'], traces[0]) + extractPath(currents[1]['value'], traces[1], False), list(traces[0])+list(traces[1])+reserves[0]+reserves[1], f"NOMERGE R:{restarts}")
    
