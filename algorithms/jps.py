import heapq
import math
import time

# 8-directional movement
DIRS = [
    (0, 1), (1, 0), (0, -1), (-1, 0),
    (1, 1), (-1, 1), (-1, -1), (1, -1)
]

def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx + dy + (math.sqrt(2) - 2) * min(dx, dy)

def isWalkable(pos, obstacles):
    return pos not in obstacles

def jump(current, direction, goal, obstacles):
    x, y = current
    dx, dy = direction
    nx, ny = x + dx, y + dy
    next_pos = (nx, ny)

    if not isWalkable(next_pos, obstacles):
        return None

    if next_pos == goal:
        return next_pos

    # Forced neighbor check
    if dx != 0 and dy != 0:  # Diagonal
        if (isWalkable((nx - dx, ny + dy), obstacles) and not isWalkable((nx - dx, ny), obstacles)) or \
           (isWalkable((nx + dx, ny - dy), obstacles) and not isWalkable((nx, ny - dy), obstacles)):
            return next_pos
    else:  # Straight
        if dx != 0:
            if (isWalkable((nx + dx, ny + 1), obstacles) and not isWalkable((nx, ny + 1), obstacles)) or \
            (isWalkable((nx + dx, ny - 1), obstacles) and not isWalkable((nx, ny - 1), obstacles)):
                return next_pos
        elif dy != 0:
            if (isWalkable((nx + 1, ny + dy), obstacles) and not isWalkable((nx + 1, ny), obstacles)) or \
            (isWalkable((nx - 1, ny + dy), obstacles) and not isWalkable((nx - 1, ny), obstacles)):
                return next_pos

    # Recursive jump
    if dx != 0 and dy != 0:
        if jump((nx, ny), (dx, 0), goal, obstacles) or jump((nx, ny), (0, dy), goal, obstacles):
            return next_pos

    return jump((nx, ny), direction, goal, obstacles)

def get_directions(prev, current):
    dx = current[0] - prev[0]
    dy = current[1] - prev[1]
    dx = 0 if dx == 0 else dx // abs(dx)
    dy = 0 if dy == 0 else dy // abs(dy)
    return [(dx, dy)] if (dx, dy) != (0, 0) else DIRS

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

def convertTreeToUniqueList (tree):
    obj = {}
    for node in tree:
        obj[f"{node[0]}:{node[1]}"] = None
    return obj

def sendData (socketInformation, cameFrom, startNode):

    if socketInformation == None:
        return

    if 'io' not in socketInformation:
        return

    path = reconstruct_path(cameFrom, startNode)
    path = convertTreeToUniqueList(path)

    parentStringEdition = convertTreeToUniqueList(cameFrom)

    if 'sleepDuration' in socketInformation:
        time.sleep(socketInformation['sleepDuration'])

    socketInformation['io'].emit('message', { 'meta':{'algorithm':'JPS',  'visitSize':len(cameFrom) }, 'gridSize':socketInformation.get('gridSize'), 'id':socketInformation.get('id'), 'path':path, 'barriers':socketInformation.get('stringBarriers'), 'visited':parentStringEdition })

def jps(start, goal, obstacles, socketInformation=None):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, None))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, cost, current, parent = heapq.heappop(open_set)
        sendData (socketInformation, came_from, current)

        if current == goal:
            return reconstruct_path(came_from, current), came_from

        directions = get_directions(parent, current) if parent else DIRS
        found_jump = False

        for dx, dy in directions:
            jp = jump(current, (dx, dy), goal, obstacles)
            if jp:
                found_jump = True
                tentative_g = g_score[current] + math.hypot(jp[0] - current[0], jp[1] - current[1])
                if jp not in g_score or tentative_g < g_score[jp]:
                    g_score[jp] = tentative_g
                    f_score = tentative_g + heuristic(jp, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, jp, current))
                    came_from[jp] = current

        # Fallback to vanilla A* if no jump point was found
        if not found_jump:
            for dx, dy in DIRS:
                neighbor = (current[0] + dx, current[1] + dy)
                if not isWalkable(neighbor, obstacles):
                    continue
                tentative_g = g_score[current] + math.hypot(dx, dy)
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor, current))
                    came_from[neighbor] = current                    

    return None, came_from  # No path found
