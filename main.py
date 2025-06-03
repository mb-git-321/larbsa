from progress.bar import Bar
import os
from util import getAreaMeta, encodeArray, findRightAngleTurns, commentResults, encodeCord
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

from algorithms.rrt import rrtRunner

import secrets
import tracemalloc

def runSingleTest (algorithm='magnetic', start=(0, 0), end=(1, 1), barriers={}, gridSize=100, comment=True):
    
    originalBarriers = barriers.copy()
    
    path = []
    
    message = ''
    if algorithm == 'da2':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = dual_astar_algorithm(originalBarriers, start, end, maxIterations=1000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'a2':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = astar_algorithm(originalBarriers, start, end, maxIterations=1000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'lee':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = lee_algorithm(originalBarriers, start, end, maxIterations=1000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'sh':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = heuristic(start, end, originalBarriers)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'shp':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = singlePruned(start, end, originalBarriers)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()        

    elif algorithm == 'm4':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4(start, end, originalBarriers, maxIterations=10000000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()  

    elif algorithm == 'm4Pythag':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magenticPythag(start, end, originalBarriers)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()  

    elif algorithm == 'm8':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic8(start, end, originalBarriers)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop() 

    elif algorithm == 'm4p':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4Pruned(start, end, originalBarriers, maxIterations=10000000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    elif algorithm == 'm4ps':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic4PrunedSpace(start, end, originalBarriers, maxIterations=10000000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()        

    elif algorithm == 'm8ps':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits, message ) = magnetic8Prunedspace(start, end, originalBarriers, maxIterations=10000000000)
        endTime = timer()
        (_, maxMemory) = tracemalloc.get_traced_memory()
        tracemalloc.stop()      

    elif algorithm == 'rrt':
        tracemalloc.start()
        tracemalloc.take_snapshot()
        startTime = timer()
        ( path, visits ) = rrtRunner(start, end, originalBarriers, gridSize, maxIterations=1000000)
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
    visitLength = len(visits)-len(path) if algorithm != 'da2' else len(visits)-len(path)-1
    results = { 'maxMemory':maxMemory, 'message':message, 'numberOfRightAngleTurns':rightAngleTurns, 'visitExcess':max(0, visitLength), 'path':path, 'duration':str(duration), 'pathSize':len(path), 'algorithm':algorithm }

    if comment:
        commentResults(results)

    return results

def runMultipleTest (testType='robustness', algorithms=['sh', 'shp', 'm4', 'm4Pythag', 'm8', 'm4p', 'm4ps', 'm8ps', 'lee', 'a2', 'da2'], robustnessPercentage=5, gridSize=50, extensionName='', overrideIterations=None, includeMessage=False):
    print('running multiple...')
    foundBarriers = {}
    iteration = 100000 if overrideIterations == None else overrideIterations
    metrics = [ 'algorithm', 'numberOfRightAngleTurns', 'visitExcess', 'duration', 'pathSize', 'maxMemory' ]
    
    if includeMessage:
        metrics.append('message')
    csv = ','.join(metrics)
    
    csv+=',start,end,barrierID,roundID,path'
    
    dissmissedCsv=[]
    bar = Bar('Processing', max=iteration)
    while iteration > 0:
        if testType == 'robustness':
            (start, end, barriers) = produceRandomMaze(robustnessPercentage, gridSize)
        elif testType == 'efficiency':
            (start, end, barriers) = efficiencyGrid(gridSize)
        else:
            (start, end, barriers) = optimalityGrid(gridSize)

        startText = encodeCord(start)
        endText = encodeCord(end)

        barrierString = list(barriers)
        barrierString.sort()
        barrierString = tuple(barrierString)

        if barrierString in foundBarriers:
            continue
        barrierID = secrets.token_urlsafe(16)
        foundBarriers[barrierString] = {'id':barrierID, 'success':False, 'start':start, 'end':end}
        restart = False
        added = 0
        for alg in algorithms:
            try:
                results = runSingleTest (alg, start, end, barriers, gridSize, False)
            except:
                restart = True
                dissmissedCsv.append(f'{alg},{foundBarriers[barrierString]}')
                break
            if results != None and len(results['path']) >= 1:
                results['path'] = encodeArray(results['path'])
                row = ','.join( [ str(results[field]) for field in metrics ] )
                extension = ','.join([startText, endText, barrierID, str(iteration), results['path']])
                row += ','+extension
                added += 1
                csv+='\n'+row
                foundBarriers[barrierString]['success'] = True
            else:
                restart = True
                dissmissedCsv.append(f'{alg},{foundBarriers[barrierString]}')
                break
        if not restart:
            row = row[:-added]
            iteration -= 1
            bar.next()
    bar.finish()

    with open(f'{os.path.dirname(__file__)}/results/{testType}_{extensionName}.csv', 'w+') as f:
        f.write(csv)

    with open(f'{os.path.dirname(__file__)}/results/{testType}_maps_{extensionName}.csv', 'w+') as f:
        plain = "id,map,success,start,end"
        for map in foundBarriers:
            plain += f'\n{foundBarriers[map]["id"]},{encodeArray(map)},{"yes" if foundBarriers[map]["success"] else "no"},{foundBarriers[map]["start"]},{foundBarriers[map]["end"]}'
        f.write(plain)        

# '''

    # If you want to run multiple algorithms, side by side and get their results, use the following code 
    # Run all three 4 lines for complete test

gridSize = 100
runMultipleTest(testType='optimality', overrideIterations=100000, gridSize=gridSize, extensionName='1')
runMultipleTest(testType='efficiency', overrideIterations=100000, gridSize=gridSize, extensionName='1')
for k in range(1, 31):
    runMultipleTest(testType='robustness', overrideIterations=1000, robustnessPercentage=k, extensionName=f'{k}%', gridSize=gridSize)

# '''

'''

    # If you just want to run one algorithm, uncomment of the first 3 functions

    # For random sample
    (start, end, barriers) = produceRandomMaze(1, gridSize)

    # For efficiency sample
    # (start, end, barriers) = efficiencyGrid(gridSize)

    # For optimality sampe
    # (start, end, barriers) = optimalityGrid(gridSize)
    
    runSingleTest('mg5', start, end, barriers, animate=False) # dual version

'''

# For random sample
(start, end, barriers) = produceRandomMaze(1, gridSize)
runSingleTest('rrt', start, end, barriers, animate=False) # dual version