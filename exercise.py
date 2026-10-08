import math
from collections import deque
import heapq


def detect_frontiers(occupancy_map, map_width, map_height):
    """
    Detects frontiers in the occupancy map.
    reference the Notes and HW for definition of frontier cells.

    Args:
        occupancy_map 2D Array: The robot's 2D map.
            - 0: Known free space
            - 1: Known occupied space
            - 0.5: Unknown space
        map_width (int): The width of the map.
        map_height (int): The height of the map.

    Returns:
        list of tuples: A list of (x, y) coordinates for each frontier cell.
    """
    """
       Hint:
          - The directions to check for neighbors are: (0,1), (0,-1), (1,0), (-1,0)
          - A frontier must be a known, open cell (value 0) that is adjacent to at least one unknown cell (value 0.5).
          - BEWARE: Be careful not to check outside the bounds of the map!
    """
    frontiers = []
    direction = [(0,1),(-1,0),(0,-1),(1,0)]
    #print("this is the map")
    # print(occupancy_map)
    # print(map_height)
    # print(map_width)

    for y in range(map_height):
        for x in range(map_width):
            if occupancy_map[y][x] == 0:
                for dx, dy in direction:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        if occupancy_map[ny][nx] == 0.5:
                            frontiers.append((x, y))
                            break
    # for i in frontiers:
    #     print("from first function")
    #     print(i)
    return frontiers

def calculate_frontier_centroids(frontiers, occupancy_map, map_width, map_height):
    """
    Groups adjacent frontier cells into clusters and calculates the centroid of each cluster.

    Args:
        frontiers (list of tuples): A list of (x, y) coordinates for each frontier cell.
        occupancy_map, map_width, map_height: Map details.

    Returns:
        list of tuples: A list of (x, y) coordinates representing the centroid of each frontier group.
    """
    # for i in frontiers:
    #     print("from second function")
    #     print(i)

    frontier_set = set(frontiers)
    visited = set()
    centroids = []
    directions = [(0,1),(-1,0),(1,0),(0,-1)]
    for cell in frontiers:
        if cell in visited:
            continue
        cluster = []
        queue = deque([cell])
        visited.add(cell)
        #print(queue)
        while queue:
            currentX, currentY = queue.popleft()
            cluster.append((currentX, currentY))
            for dx, dy in directions:
                nbr = (currentX + dx, currentY + dy)
                if nbr in frontier_set and nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)
        # print("Cluster")
        # print(cluster)
        averageX = sum(x for x, _ in cluster) / len(cluster)
        averageY = sum(y for _, y in cluster) / len(cluster)
        centroids.append((averageX, averageY))
        #print(averageX, averageY)

    # print("Centroids")
    # print(centroids)
    # print("Visited")
    # print(visited)
    return centroids
def get_next_closet_actions(node, goal_cell, occupancy_map, map_width, map_height):
    directions = [(0, 1), (-1, 0), (1, 0), (0, -1)]
    neighbors = []
    for (dx, dy) in directions:
        nx = node[0] + dx
        ny = node[1] + dy
        if 0 <= nx < map_width and 0 <= ny < map_height:
            #print("Occupancy:",occupancy_map[ny][nx])
            if occupancy_map[ny][nx] == 0 or (nx, ny) == goal_cell:
                neighbors.append(((nx, ny), 1))
    #print("Neighbors:",neighbors)
    return neighbors
def cal_astar(start, goal, occupancy_map, map_width, map_height):
    start_cell = (int(round(start[0])), int(round(start[1])))
    goal_cell = (int(round(goal[0])), int(round(goal[1])))
    open_set = [(math.hypot(start_cell[0] - goal_cell[0], start_cell[1] - goal_cell[1]) , start_cell)]

    came_from = {}
    g_score = {start_cell: 0.0}
    while open_set:
        f, current = heapq.heappop(open_set)
        #print("current: ",current)
        if current == goal_cell:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            #print(path)
            return path, g_score[goal_cell]
        for neighbor, step_cost in get_next_closet_actions(current, goal_cell, occupancy_map, map_width, map_height):
            tentative_g = g_score[current] + step_cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + math.hypot(neighbor[0] - goal_cell[0], neighbor[1] - goal_cell[1])
                heapq.heappush(open_set, (f_score, neighbor))
    return None, float('inf')
def find_closest_frontier(robot_pos, frontier_centroids, occupancy_map, map_width, map_height):
    """
    Finds the frontier centroid that is closest to the robot and reachable.
    This function should use a pathfinding algorithm like A* to find a path.

    Args:
        robot_pos (tuple): The (x, y) position of the robot.
        frontier_centroids (list of tuples): Centroids of frontier groups.
        occupancy_map: The robot's 2D map.
        map_width (int): The width of the map.
        map_height (int): The height of the map.

    Returns:
        tuple or None: A tuple containing (target_goal, path_to_goal)
                       - target_goal: The (x, y) coordinate of the chosen frontier goal.
                       - path_to_goal: A list of (x, y) coordinates from robot to goal.
                       Returns (None, []) if no frontiers are reachable.
    """
    target_goal = None
    path_to_goal = []
    min_cost = float('inf')

    for centroid in frontier_centroids:
        goal = (int(round(centroid[0])), int(round(centroid[1])))
        if goal == robot_pos:
            continue
        path, path_cost = cal_astar(robot_pos, centroid, occupancy_map, map_width, map_height)
        # print(path_cost)
        # print(path)
        if path and path_cost < min_cost:
            min_cost = path_cost
            target_goal = goal
            path_to_goal = path
            # print("target",target_goal)
            # print("path",path_to_goal)
    if target_goal is None:
        return None, []

    return target_goal, path_to_goal
