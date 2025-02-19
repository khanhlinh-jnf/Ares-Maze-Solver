import time
import tracemalloc as trlloc
from collections import deque
import queue as q

Player = "@"
Switch = "."
Space = " "
Stone = "$"
Wall = "#"
Swarm_w = 2
Convergent_Swarm_w = 20


def load_maze(file_path):
    ares_position = (0, 0)
    stone_positions = []
    switch_positions = []
    index_wall = []
    stones_value = {}

    with open(file_path, "r") as file:
        value = file.readline().strip()
        value_of_stones = list(map(int, value.split()))
        data = file.readlines()
        index = 0
        for i in range(len(data)):
            for j in range(len(data[i])):
                if data[i][j] == Player:
                    ares_position = (i, j)
                elif data[i][j] == Stone:
                    stone_positions.append((i, j))
                    stones_value[(i, j)] = value_of_stones[index]
                    index = index + 1
                elif data[i][j] == Switch:
                    switch_positions.append((i, j))
                elif data[i][j] == Wall:
                    index_wall.append((i, j))
                elif data[i][j] == "*":
                    switch_positions.append((i, j))
                    stone_positions.append((i, j))
                    stones_value[(i, j)] = value_of_stones[index]
                    index = index + 1
    return ares_position, stone_positions, switch_positions, index_wall, stones_value


def check_deadlock(new_stones, index_wall, switch_positions):
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for stone in new_stones:
        i, j = stone
        if stone in switch_positions:
            continue
        for di, dj in dirs:
            ni, nj = i + di, j + dj
            if (ni, nj) in index_wall or (ni, nj) in new_stones:
                if ((i + di, j) in index_wall or (i + di, j) in new_stones) and (
                    (i, j + dj) in index_wall or (i, j + dj) in new_stones
                ):
                    return True

            if (i + di, j) in index_wall and (i, j + dj) in index_wall:
                return True

            if (i + di, j) in new_stones and (i, j + dj) in new_stones:
                if (i - di, j + dj) in index_wall and (
                    i + di,
                    j - dj,
                ) in index_wall:
                    return True

            if (i, j + dj) in new_stones and (i + di, j) in index_wall:
                if (i - di, j + dj) in index_wall:
                    return True

            if (i, j + dj) in index_wall and (i + di, j) in new_stones:
                if (i + di, j - dj) in index_wall:
                    return True
    return False


def calculate_heuristics(new_stones, new_x, new_y, new_stones_value, switch_positions):
    heuristics = 0
    Ares_to_stone = 1e9
    p_frontier = q.PriorityQueue()
    for stone in new_stones:
        p_frontier.put((-new_stones_value[stone], stone))
        distance = abs(new_x - stone[0]) + abs(new_y - stone[1])
        if distance < Ares_to_stone:
            Ares_to_stone = distance
    used = set()
    while not p_frontier.empty():
        stone = p_frontier.get()[1]
        distance = 1e9
        match = (0, 0)
        for switch in switch_positions:
            if switch in used:
                continue
            if abs(switch[0] - stone[0]) + abs(switch[1] - stone[1]) < distance:
                distance = abs(switch[0] - stone[0]) + abs(switch[1] - stone[1])
                match = switch
        used.add(match)
        heuristics += distance * new_stones_value[stone]
    heuristics += Ares_to_stone
    return heuristics


def bfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    switch_positions = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = deque()
    frontier.append((ares_position, frozenset(stone_positions), "", 0, stones_value))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.popleft()

        if stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }
        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))

        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if new_stones == switch_positions:
                end_time = time.time()
                _, memory = trlloc.get_traced_memory()
                trlloc.stop()
                return {
                    "Step": len(new_path),
                    "Weight": new_cost,
                    "Node": nodes_explored,
                    "Path": new_path,
                    "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                    "Memory": "{:.2f}".format(memory / (1024 * 1024)),
                }

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.append(
                    (
                        (new_x, new_y),
                        frozenset(new_stones),
                        new_path,
                        new_cost,
                        new_stones_value,
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def dfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    switch_positions = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 1
    frontier = q.LifoQueue()
    frontier.put((ares_position, frozenset(stone_positions), "", 0, stones_value))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()
        if stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }
        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        
        for next_x, next_y, move in [
            (-1, 0, "u"),
            (1, 0, "d"),
            (0, -1, "l"),
            (0, 1, "r"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if new_stones == switch_positions:
                end_time = time.time()
                _, memory = trlloc.get_traced_memory()
                trlloc.stop()
                return {
                    "Step": len(new_path),
                    "Weight": new_cost,
                    "Node": nodes_explored,
                    "Path": new_path,
                    "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                    "Memory": "{:.2f}".format(memory / (1024 * 1024)),
                }

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        (new_x, new_y),
                        frozenset(new_stones),
                        new_path,
                        new_cost,
                        new_stones_value,
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def ucs(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    switch_positions = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0, stones_value)))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()[1]
        if stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))

        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost,
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                            new_stones_value,
                        ),
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def astar(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    goal = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0, stones_value)))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()[1]
        if stones == goal:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))

        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost
                        + calculate_heuristics(
                            new_stones, new_x, new_y, new_stones_value, switch_positions
                        ),
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                            new_stones_value,
                        ),
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def gbfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    goal = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0, stones_value)))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()[1]
        if stones == goal:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))

        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        calculate_heuristics(
                            new_stones, new_x, new_y, new_stones_value, switch_positions
                        ),
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                            new_stones_value,
                        ),
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def swarm(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    goal = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0, stones_value)))
    explored = set()

    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()[1]
        if stones == goal:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))

        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue

            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost

            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue

                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost
                        + calculate_heuristics(
                            new_stones, new_x, new_y, new_stones_value, switch_positions
                        )
                        * Swarm_w,
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                            new_stones_value,
                        ),
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No Solution"


def convergent_swarm(file_path):
    ares_position, stone_positions, switch_positions, index_wall, stones_value = (
        load_maze(file_path)
    )
    goal = set(switch_positions)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0, stones_value)))
    explored = set()
    while frontier:
        (ax, ay), stones, path, cost, value = frontier.get()[1]
        if stones == goal:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            return {
                "Step": len(path),
                "Weight": cost,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }
        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        for next_x, next_y, move in [
            (-1, 0, "u"),
            (0, -1, "l"),
            (0, 1, "r"),
            (1, 0, "d"),
        ]:
            (new_x, new_y) = (ax + next_x, ay + next_y)
            if (new_x, new_y) in index_wall:
                continue
            new_stones = set(stones)
            new_stones_value = value.copy()
            new_path = path
            new_cost = cost
            if (new_x, new_y) in stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in stones:
                    continue
                new_cost += new_stones_value[(new_x, new_y)]
                new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop(
                    (new_x, new_y)
                )
                new_stones.add((new_stone_x, new_stone_y))
                new_stones.remove((new_x, new_y))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move
            if not check_deadlock(new_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost
                        + calculate_heuristics(
                            new_stones, new_x, new_y, new_stones_value, switch_positions
                        )
                        * Convergent_Swarm_w,
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                            new_stones_value,
                        ),
                    )
                )
                nodes_explored = nodes_explored + 1
    return "No solution"


