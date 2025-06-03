from collections import deque
import time

def keysVersion (arr, appen=False):
    obj = {} if not appen else []
    for x in arr:
        if appen:
            obj.append(f'{x[0]}:{x[1]}')
        else:
            obj[f'{x[0]}:{x[1]}']=None
    return obj

def lee_algorithm(grid, start, end, maxIterations=1000, socketInformation=None):
    queue = deque()
    queue.append(start)
    visited = [start]
    distance = {start: 0}
    path = [end]
    
    while queue and maxIterations>=0:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
                distance[neighbor] = distance[current] + 1
        maxIterations -= 1

        if socketInformation != None and 'io' in socketInformation:
            if 'sleepDuration' in socketInformation:
                time.sleep(socketInformation['sleepDuration'])            
            socketInformation['io'].emit('message', { 'meta':{'algorithm':'Lee algorithm', 'visitSize':len(visited)}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{}, 'visited':{ f'{x[0]}:{x[1]}':None for x in visited} })

                
    if end not in distance:
        return ([], visited)
    
    while path[-1] != start:
        current = path[-1]
        neighbors = get_neighbors(grid, current)
        neighbor_distances = [distance.get(n, float('inf')) for n in neighbors]
        min_distance = min(neighbor_distances)
        if min_distance == float('inf'):
            return ([], visited)
        min_neighbors = [n for i, n in enumerate(neighbors) if neighbor_distances[i] == min_distance]
        path.append(min_neighbors[0])

    if socketInformation != None and 'io' in socketInformation:
        if 'sleepDuration' in socketInformation:
            time.sleep(socketInformation['sleepDuration'])            
        socketInformation['io'].emit('message', { 'meta':{'algorithm':'Lee algorithm', 'visitSize':len(visited)}, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'barriers':socketInformation.get('stringBarriers'), 'path':{f'{x[0]}:{x[1]}':None for x in path}, 'visited':{ f'{x[0]}:{x[1]}':None for x in visited} })

        
    return (path[::-1], visited)
        
def get_neighbors(grid, current):
    row, col = current
    neighbors = []
    for r, c in ((row-1, col), (row, col-1), (row+1, col), (row, col+1)):
        if (r, c) in grid:
            continue
        neighbors.append((r, c))
    return neighbors
