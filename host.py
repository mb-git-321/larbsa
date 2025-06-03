from util import findRightAngleTurns, convertTo2Dp, turnIntoKiloBytes
from timeit import default_timer as timer
from automate.efficiency import buildBlockMaze as efficiencyGrid
from automate.optimality import produceGrid as optimalityGrid
from automate.robustness import produceRandomMaze

from algorithms.sh import heuristic
from algorithms.shp import heuristic as singlePruned
from algorithms.m4 import heuristic as magnetic4
from algorithms.m4Pythag import heuristic as magenticPythag
from algorithms.m8 import heuristic as magnetic8
from algorithms.m4p import heuristic as magnetic4Pruned
from algorithms.m4ps import heuristic as magnetic4PrunedSpace
from algorithms.m8ps import heuristic as magnetic8Prunedspace

from algorithms.lee import lee_algorithm
from algorithms.a2 import astar_algorithm
from algorithms.da2 import dual_astar_algorithm

import tracemalloc
import socketio
import threading

runningFunction = False

# Connect to the Socket.IO server
sio = socketio.Client()
sio.connect('http://localhost:9000')

# Define event handlers
@sio.on('connect')
def on_connect():
    print('Connected to Socket.IO server')

@sio.on('message')
def on_message(data):
    if runningFunction:
        return
    if 'nonprocessing' not in data:
        return 
    runComponents (data['algorithms'], data['gridSize'], data['rosbustnessLevel'], data['testType'], None if 'seedValue' not in data else data['seedValue'], 0.05 if 'delay' not in data else data['delay'])

event_thread = threading.Thread(target=sio.wait)
event_thread.start()

def runSingleTest (algorithm='magnetic', start=(0, 0), end=(1, 1), barriers={}, socketInformation=None):
    originalBarriers = barriers.copy()
    path = []
    message = ''
    # barriers = getAreaMeta(barriers, areaSize) if algorithm == 'magnetic' or algorithm == 'lee' or algorithm == 'mg6' else barriers
    
    if algorithm == 'da2':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = dual_astar_algorithm(originalBarriers, start, end, maxIterations=1000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'a2':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = astar_algorithm(originalBarriers, start, end, maxIterations=1000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'lee':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = lee_algorithm(originalBarriers, start, end, maxIterations=1000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'sh':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = heuristic(start, end, originalBarriers, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'shp':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = singlePruned(start, end, originalBarriers, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()        

    elif algorithm == 'm4':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4(start, end, barriers, maxIterations=10000000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()  

    elif algorithm == 'm4Pythag':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magenticPythag(start, end, barriers)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()  

    elif algorithm == 'm8':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic8(start, end, barriers, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop() 

    elif algorithm == 'm4p':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4Pruned(start, end, barriers, maxIterations=10000000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'm4ps':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4PrunedSpace(start, end, barriers, maxIterations=10000000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()        

    elif algorithm == 'm8ps':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic8Prunedspace(start, end, barriers, maxIterations=10000000000, socketInformation=socketInformation)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()         
      
    else:
        startTime = 0
        endTime = 0

    if path == -1 or path == None or ( type(path)==list and not len(path) ):
        return None

    rightAngleTurns = findRightAngleTurns(path)
    duration = endTime - startTime
    pathSize = len(path) if algorithm != 'da2' else len(path)-1
    if socketInformation != None and 'io' in socketInformation:
        socketInformation['io'].emit('message', { 'meta':{'pathSize':pathSize, 'numberOfRightAngleTurns':rightAngleTurns, 'visitSize':len(visits), 'run time with delay':str(convertTo2Dp(duration)) }, 'id':socketInformation.get('id') })

    results = { 'maxMemory':maxMemory, 'message':message, 'numberOfRightAngleTurns':rightAngleTurns, 'visitExcess':max(0, len(visits)-len(path)), 'path':path, 'duration':duration, 'pathSize':pathSize, 'algorithm':algorithm }

    return results

def runComponents (algorithms=[], gridSize=50, rosbustnessLevel=20, testType='robustness', seedValue=None, delay=0.05):
    
    global runningFunction
    
    print('Triggered by socket to run algorithms in parallel...')

    runningFunction = True

    if testType=='robustness':
        (start, end, barriers) = produceRandomMaze(rosbustnessLevel, gridSize, seedValue)
    elif testType=='efficiency':
        (start, end, barriers) = efficiencyGrid(gridSize, seedValue)
    else:
        (start, end, barriers) = optimalityGrid(gridSize, seedValue)

    stringBarriers = { f'{j[0]}:{j[1]}':None for j in barriers }
    threadObjects = []
    for i in range(len(algorithms)):
        algo = algorithms[i]
        socketInfo = { 'id':i, 'io':sio, 'sleepDuration':delay/1000, 'stringBarriers':stringBarriers, 'gridSize':gridSize }
        t1 = threading.Thread(target=runSingleTest, args=(algo, start, end, barriers, socketInfo))
        threadObjects.append(t1)

    for thr in threadObjects:
        thr.start()

    for thr in threadObjects:
        thr.join()

    for i in range(len(algorithms)):
        algo = algorithms[i]
        results = runSingleTest(algo, start, end, barriers, None)
        if results == None:
            continue

        sio.emit('message', { 'meta':{ 'maxMemory': str(turnIntoKiloBytes(results['maxMemory'])) + ' kb' , 'real run time':str( convertTo2Dp(results['duration']*1000) ) + 'milli-seconds' }, 'id':i })
        
    runningFunction = False
