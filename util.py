import math

def convertTo2Dp (numb):
    return math.floor(numb*100)/100

def getAreaMeta (blockers, areaSize):
    areaMeta = {}
    for key in blockers:
        x = math.floor((key[0])/areaSize)
        y = math.floor((key[1])/areaSize)
        id = (x,y)
        if id in areaMeta:
            areaMeta[id][key] = None
        else:
            areaMeta[id] = {}
            areaMeta[id][key] = None

    return areaMeta

def turnIntoKiloBytes (bytes):
    # inKiloBytes = bytes / 1000
    return math.floor(bytes*10)/10000

def getDistance(vectorOne, vectorTwo, pythagoras=True):
    if not pythagoras:
        return abs(vectorOne[0]-vectorTwo[0]) + abs(vectorOne[1]-vectorTwo[1])  
    return math.sqrt(math.pow(vectorOne[0]-vectorTwo[0], 2) + math.pow(vectorOne[1]-vectorTwo[1], 2))

def findRightAngleTurns (path):
    numberOfTurns = 0
    for k in range(2, len(path)):
        current = path[k]
        prev = path[k-2]
        difference = (abs(current[0]-prev[0]), abs(current[1]-prev[1]))
        if difference[0] >= 1 and difference[1] >= 1:
            numberOfTurns += 1
    return numberOfTurns

def calculateAverageDistanceFromObstacles (path, obstacles):
    distances = [1, 2]
    for cord in path:
        distances.append(findClosestObstacle(cord, obstacles))
    
    # distances.sort()
    size = len(distances)
    return sum(distances)/size
    # [math.floor(size/2)]    

def encodeCord (cord, cordSplitter="::"):
    try:
        return str(cord[0])+cordSplitter+str(cord[1])
    except:
        True
        return ""

def findClosestObstacle (cord, obstacles):
    keys = list(obstacles)
    min_ = float('inf')
    for ob in keys:
        distance = getDistance(ob, cord, pythagoras=False)
        min_ = min(min_, distance)
    
    return min_

def encodeArray (arr, cordListSplitter=":::", cordSplitter="::"):
    return cordListSplitter.join( [ encodeCord(cord, cordSplitter) for cord in arr ] )     

def findRightAngleTurns (path):
    numberOfTurns = 0
    for k in range(2, len(path)):
        current = path[k]
        prev = path[k-2]
        difference = (abs(current[0]-prev[0]), abs(current[1]-prev[1]))
        if difference[0] >= 1 and difference[1] >= 1:
            numberOfTurns += 1
    return numberOfTurns    

def commentResults (results):
    # print('--------------------------------------------------------------------\n')
    for key in results:
        if key == 'path':
            continue
        print(key.upper()+': '+( str(results[key])))
    print('--------------------------------------------------------------------')


def decode (node):

    try:
        first = int(node[0])
    except:
        first = -1 * int( node[0].replace('-', '') )

    try:
        second = int(node[1])
    except:
        second = -1 * int( node[1].replace('-', '') )

    return (first, second)

# f = open("reproduce.txt", "r")
# ( barrierString, start, end ) = f.read().split(',')
# barriersTemp = [ decode( x.split('::') ) for x in barrierString.split(':::') ]
# barriers = {}
# def setX(x):
#     barriers[x]=None
# [setX(x) for x in barriersTemp]
# start = decode(start.split('::'))
# end = decode(end.split('::'))

# f = open("mg4errormap3.txt", "r")
# barrierString = f.read()
# barriersTemp = [ decode( x.split('::') ) for x in barrierString.split(':::') ]
# barriers = {}
# def setX(x):
#     barriers[x]=None
# [setX(x) for x in barriersTemp]
# start = (0, 0)
# end = (49, 48)

# print(barrierString)
# runMultipleTest(testType='efficiency', extensionName='Test101')
# runMultipleTest(testType='optimality')
# runSingleTest('mg4', start, end, barriers, areaSize, blockSize, gridSize)
# time.sleep(5)

# runSingleTest('mg4', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('mg5', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('mg11', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('mg12', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('lee', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('a2', start, end, barriers, areaSize, blockSize, gridSize)


# runSingleTest('a2', start, end, barriers, areaSize, blockSize, gridSize)
# runSingleTest('lee', start, end, barriers, areaSize, blockSize, gridSize)
