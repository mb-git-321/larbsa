import heapq
import time

def keysVersion (arr, appen=False):
    obj = {} if not appen else []
    for x in arr:
        if appen:
            obj.append(f'{x[0]}:{x[1]}')
        else:
            obj[f'{x[0]}:{x[1]}']=None
    return obj

def findPath (start, end, came_from):
    path = []
    current = end
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    return (path[::-1], came_from)    

def dual_astar_algorithm(grid, start, end, maxIterations=1000, socketInformation=None):
    heaps = ([], [])
    
    tempHeap = [] if socketInformation else None

    destinations = (end, start)

    heapq.heappush(heaps[0], (0, start))
    heapq.heappush(heaps[1], (0, end))

    came_from = ({}, {})
    cost_so_far = ({}, {})

    came_from[0][start] = None
    cost_so_far[0][start] = 0

    came_from[1][end] = None
    cost_so_far[1][end] = 0    
    
    index = 0

    conjoinedPoint = None

    while (heaps[0] or heaps[1]) and conjoinedPoint == None and maxIterations >= 1000:
        nextIndex = (index + 1 ) % 2
        current = heapq.heappop(heaps[index])[1] if len(heaps[index]) else None
        if current == destinations[index] or current == None:
            break
        
        for neighbor in get_neighbors(grid, current):
            new_cost = cost_so_far[index][current] + distance(current, neighbor)
            if neighbor not in cost_so_far[index] or new_cost < cost_so_far[index][neighbor]:
                cost_so_far[index][neighbor] = new_cost
                priority = new_cost + distance(neighbor, destinations[index])
                heapq.heappush(heaps[index], (priority, neighbor))
                
                if socketInformation:
                    tempHeap.append(neighbor)

                if neighbor in came_from[nextIndex]:
                    conjoinedPoint = neighbor

                came_from[index][neighbor] = current

        if socketInformation != None and 'io' in socketInformation:
            if 'sleepDuration' in socketInformation:
                time.sleep(socketInformation['sleepDuration'])  
                # 'conjoinedPoint':f'{conjoinedPoint[0]}, {conjoinedPoint[1]}' if conjoinedPoint != None else 'Waiting...'          
            socketInformation['io'].emit('message', { 'meta':{'algorithm':'A2 algorithm', 'visitSize':len(tempHeap) }, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{}, 'visited':{ f'{x[0]}:{x[1]}':None for x in tempHeap} })

        maxIterations -= 1
        index = nextIndex

    if conjoinedPoint==None and end not in came_from:
        return ([], came_from[0])
    
    
    path = []
    if conjoinedPoint != None:
        pathA = []        
        pathB = []        
        current = conjoinedPoint
        while current != start:
            pathA.append(current)
            current = came_from[0][current]
        current = conjoinedPoint
        while current != end:
            pathB.append(current)
            current = came_from[1][current]

        pathA.append(start)
        pathB.append(end)
        path = pathA[::-1] + pathB

        if socketInformation != None and 'io' in socketInformation:
            if 'sleepDuration' in socketInformation:
                time.sleep(socketInformation['sleepDuration'])            
            socketInformation['io'].emit('message', { 'meta':{'algorithm':'Dual A2 algorithm', 'visitSize':len(tempHeap)}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{f'{x[0]}:{x[1]}':None for x in path}, 'visited':{ f'{x[0]}:{x[1]}':None for x in tempHeap} })

        return (path, { x:None for x in list(came_from[0])+list(came_from[1]) })

    else:

        current = end
        while current != start:
            path.append(current)
            current = came_from[index][current]
            
            if socketInformation != None and 'io' in socketInformation:
                if 'sleepDuration' in socketInformation:
                    time.sleep(socketInformation['sleepDuration'])            
                socketInformation['io'].emit('message', { 'meta':{'algorithm':'Dual A2 algorithm', 'visitSize':len(tempHeap)}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{f'{x[0]}:{x[1]}':None for x in path}, 'visited':{ f'{x[0]}:{x[1]}':None for x in tempHeap} })

    path.append(start)
    if socketInformation != None and 'io' in socketInformation:
        if 'sleepDuration' in socketInformation:
            time.sleep(socketInformation['sleepDuration'])            
        socketInformation['io'].emit('message', { 'meta':{'algorithm':'Dual A2 algorithm', 'visitSize':len(tempHeap)}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{f'{x[0]}:{x[1]}':None for x in path}, 'visited':{ f'{x[0]}:{x[1]}':None for x in tempHeap} })


    return (path[::-1], came_from[0])

def get_neighbors(grid, current):
    row, col = current
    neighbors = []
    for r, c in ((row-1, col), (row, col-1), (row+1, col), (row, col+1)):
        if (r, c) in grid:
            continue
        neighbors.append((r, c))
    return neighbors

def distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)
