import random
import math
import matplotlib.pyplot as plt

# Utility Functions
def create_node(x, y, parent=None):
    return {'x': x, 'y': y, 'parent': parent}

def distance(n1, n2):
    return math.hypot(n1['x'] - n2['x'], n1['y'] - n2['y'])

def random_position(x_limit, y_limit):
    return create_node(random.uniform(0, x_limit), random.uniform(0, y_limit))

def is_in_obstacle(point, obstacles):
    for (ox, oy, r) in obstacles:
        if math.hypot(point['x'] - ox, point['y'] - oy) <= r:
            return True
    return False

def nearest_node(tree, new_node):
    return min(tree, key=lambda n: distance(n, new_node))

def steer(from_node, to_node, step_size):
    dist = distance(from_node, to_node)
    if dist < step_size:
        return to_node
    theta = math.atan2(to_node['y'] - from_node['y'], to_node['x'] - from_node['x'])
    new_x = from_node['x'] + step_size * math.cos(theta)
    new_y = from_node['y'] + step_size * math.sin(theta)
    return create_node(new_x, new_y, parent=from_node)

def is_goal(node, goal_center, goal_radius):
    return distance(node, goal_center) <= goal_radius

def draw_path(node):
    path = []
    while node:
        path.append((node['x'], node['y']))
        node = node['parent']
    return path[::-1]

def plot_rrt(tree, path, start, goal_center, goal_radius, obstacles):
    for node in tree:
        if node['parent']:
            plt.plot([node['x'], node['parent']['x']],
                     [node['y'], node['parent']['y']], "-g")

    if path:
        px, py = zip(*path)
        plt.plot(px, py, "-r", linewidth=2)

    plt.plot(start['x'], start['y'], "bo", label="Start")
    plt.plot(goal_center['x'], goal_center['y'], "ro", label="Goal Center")
    plt.gca().add_patch(plt.Circle((goal_center['x'], goal_center['y']), goal_radius, color='r', alpha=0.3))

    for ox, oy, r in obstacles:
        plt.gca().add_patch(plt.Circle((ox, oy), r, color='k', alpha=0.5))

    plt.axis('equal')
    plt.grid(True)
    plt.title("Functional RRT Path Planning")
    plt.legend()
    plt.show()

# Main RRT Function
def rrt(start, goal_center, goal_radius, obstacles, x_limit, y_limit, max_iter=500, step_size=10):
    tree = [start]
    for _ in range(max_iter):
        rnd = random_position(x_limit, y_limit)
        if is_in_obstacle(rnd, obstacles):
            continue
        nearest = nearest_node(tree, rnd)
        new_node = steer(nearest, rnd, step_size)
        if is_in_obstacle(new_node, obstacles):
            continue
        tree.append(new_node)
        if is_goal(new_node, goal_center, goal_radius):
            print("Goal reached!")
            return tree, new_node
    print("Goal not reached.")
    return tree, None

def rrtRunner (start, end, obstacles, gridSize):
    start = create_node(start[0], start[1])
    goal_center = create_node(end[0], end[1])
    goal_radius = 1
    x_limit, y_limit = gridSize, gridSize
    tree, goal_node = rrt(start, goal_center, goal_radius, obstacles, x_limit, y_limit)
    path = draw_path(goal_node) if goal_node else None
    return path, tree
