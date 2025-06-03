import time

"""
    MG5 can find a path between two nodes, with heuristic, with the magnetism enabled 
    This version makes use of 8 options instead of 4 
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
        if nodes[currentlyAt] in path:
            return []
        path.append(nodes[currentlyAt])
        
        currentlyAt = nodes[currentlyAt]

    return path[::-1] if reverse else path

def getExtraOptions (current, visited, obstacles):
    options = []
    top = True
    right = True
    left = True
    bottom = True
    # top is free
    if filterOptions((current[0]-1, current[1]), visited, obstacles):
        options.append((current[0]-1, current[1]))
    else:
        top = False

    # right is free
    if filterOptions((current[0], current[1]+1), visited, obstacles):
        options.append((current[0], current[1]+1))
    else:
        right = False

    # bottom is free
    if filterOptions((current[0]+1, current[1]), visited, obstacles):
        options.append((current[0]+1, current[1]))
    else:
        bottom = False 

    # left is free
    if filterOptions((current[0], current[1]-1), visited, obstacles):
        options.append((current[0], current[1]-1))
    else:
        left = False

    if top and left:
        if filterOptions((current[0]-1, current[1]-1), visited, obstacles):
            options.append((current[0]-1, current[1]-1)) 
    if top and right:
        if filterOptions((current[0]-1, current[1]+1), visited, obstacles):
            options.append((current[0]-1, current[1]+1)) 
    if bottom and left:
        if filterOptions((current[0]+1, current[1]-1), visited, obstacles):
            options.append((current[0]+1, current[1]-1))  
    if bottom and right:
        if filterOptions((current[0]+1, current[1]+1), visited, obstacles):
            options.append((current[0]+1, current[1]+1))

    return options                                     

# def runSingleIteration (currentInfo, queue, reserves, visitedTrace, visited, vistedNext, end, obstacles):
def runSingleIteration (currentInfo, queue, reserves, visitedTrace, vistedNext, end, obstacles):

    currentInfo['value'] = queue.pop(0) 
    current = currentInfo['value']
    options = getExtraOptions(current, visitedTrace, obstacles)

    if not len(options) and len(reserves):
        # this is when we know we have rerouted since we are no longer taking the best option
        (parent, nextRes) = reserves.pop(0)
        # visited.append(nextRes)
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
        fitness = abs(opt[0] - end[0]) + abs(opt[1] - end[1]) 
        if fitness < bestFitness:
            bestFitness = fitness
            bestCord = opt

    # visited.append(bestCord)
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

def convertTracesIntoSingleObj (traces):
    return { f'{x[0]}:{x[1]}':None for x in list(traces[0]) + list(traces[1]) }

def heuristic(start, end, barriers, maxIterations=100000, socketInformation=None): #function for something else
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

            if socketInformation != None:
                if 'sleepDuration' in socketInformation:
                    time.sleep(socketInformation['sleepDuration'])
                path = extractPath(currents[index]['value'], traces[index]) + extractPath(currents[nextIndex]['value'], traces[nextIndex], False)
                path = { f'{x[0]}:{x[1]}':None for x in path }
                if 'io' in socketInformation:
                    socketInformation['io'].emit('message', { 'meta':{'algorithm':'Magnetic algorithm (with 8 options)'}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'path':path, 'barriers':socketInformation.get('stringBarriers'), 'visited':convertTracesIntoSingleObj(traces) })

            index = nextIndex
            maxIterations -= 1
        except Exception as e:
            return ([], [], "")

    if maxIterations <= 0:
        return ([], [], "PASSED-MAX-ITERATIONS")

    if mergePoint != None:
        p1 = extractPath(mergePoint, traces[0])
        p2 = extractPath(mergePoint, traces[1], False)
        path = p1 + p2[1:] 
        
        if socketInformation != None and 'io' in socketInformation:
            tempPath = { f'{x[0]}:{x[1]}':None for x in path }
            socketInformation['io'].emit('message', { 'meta':{'algorithm':'Magnetic algorithm (with 8 options)'}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':tempPath, 'visited':convertTracesIntoSingleObj(traces) })

        return (path, list(traces[0])+list(traces[1])+reserves[0]+reserves[1], f"MERGEPOINT R:{restarts}")

    path = extractPath(currents[0]['value'], traces[0]) + extractPath(currents[1]['value'], traces[1], False)

    if socketInformation != None and 'io' in socketInformation:
        tempPath = { f'{x[0]}:{x[1]}':None for x in path }
        socketInformation['io'].emit('message', { 'meta':{'algorithm':'Magnetic algorithm (with 8 options)'}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':tempPath, 'visited':convertTracesIntoSingleObj(traces) })

    return (path, list(traces[0])+list(traces[1])+reserves[0]+reserves[1], f"NOMERGE R:{restarts}")
    
