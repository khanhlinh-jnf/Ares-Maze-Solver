import time
import tracemalloc as trlloc
from collections import deque
import queue as q

OVERTIME = 300

Player = "@"
Switch = "."
Space = " "
Stone = "$"
Wall = "#"
weighted_astar_w = 5


def load_maze(file_path):
    ares_position = (0, 0)
    stone_positions = set()
    switch_positions = set()
    index_wall = set()

    with open(file_path, "r") as file:
        value = file.readline().strip()
        value_of_stones = list(map(int, value.split()))
        data = file.readlines()
        index = 0
        for i in range(len(data)):
            for j in range(len(data[i])):
                if data[i][j] == Player:
                    ares_position = (i, j)
                elif data[i][j] == "+":
                    ares_position = (i, j)
                    switch_positions.add((i, j))
                elif data[i][j] == Stone:
                    w = value_of_stones[index]
                    stone_positions.add((i, j, w))
                    index = index + 1
                elif data[i][j] == Switch:
                    switch_positions.add((i, j))
                elif data[i][j] == Wall:
                    index_wall.add((i, j))
                elif data[i][j] == "*":
                    w = value_of_stones[index]
                    switch_positions.add((i, j))
                    stone_positions.add((i, j, w))
                    index = index + 1
    return ares_position, stone_positions, switch_positions, index_wall

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

    return False

def calculate_heuristics(new_stones, new_x, new_y, switch_positions):
    total_heuristic = 0
    distance_ares_to_stone_min = 1e10
    for stone in new_stones:
        i, j, w = stone
        distance_ares_to_stone_min = min(
            distance_ares_to_stone_min, abs(new_x - i) + abs(new_y - j)
        )
        cost = 1e9
        for switch in switch_positions:
            cost = min(cost, abs(i - switch[0]) + abs(j - switch[1]))
        total_heuristic += cost * w

    return total_heuristic + distance_ares_to_stone_min - 1


def bfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.Queue()
    frontier.put((ares_position, frozenset(stone_positions), "", 0))
    explored = set()
    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):

                set_of_new_stones = set()
                for stone in new_stones:
                    i, j, w = stone
                    set_of_new_stones.add((i, j))

                if set_of_new_stones == switch_positions:
                    end_time = time.time()
                    _, memory = trlloc.get_traced_memory()
                    trlloc.stop()
                    step_not_push_stone = 0
                    for c in new_path:
                        if c.islower():
                            step_not_push_stone += 1
                    return {
                        "Step": len(new_path),
                        "Weight": new_cost - step_not_push_stone,
                        "Node": nodes_explored,
                        "Path": new_path,
                        "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                        "Memory": "{:.2f}".format(memory / (1024 * 1024)),
                    }

                frontier.put(
                    (
                        (new_x, new_y),
                        frozenset(new_stones),
                        new_path,
                        new_cost,
                    ),
                )

    return "No Solution"

def dfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.LifoQueue()
    frontier.put((ares_position, frozenset(stone_positions), "", 0))
    explored = set()

    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):

                set_of_new_stones = set()
                for stone in new_stones:
                    i, j, w = stone
                    set_of_new_stones.add((i, j))

                if set_of_new_stones == switch_positions:
                    end_time = time.time()
                    _, memory = trlloc.get_traced_memory()
                    trlloc.stop()
                    step_not_push_stone = 0
                    for c in new_path:
                        if c.islower():
                            step_not_push_stone += 1
                    return {
                        "Step": len(new_path),
                        "Weight": new_cost - step_not_push_stone,
                        "Node": nodes_explored,
                        "Path": new_path,
                        "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                        "Memory": "{:.2f}".format(memory / (1024 * 1024)),
                    }

                frontier.put(
                    (
                        (new_x, new_y),
                        frozenset(new_stones),
                        new_path,
                        new_cost,
                    ),
                )

    return "No Solution"

def ucs(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0)))
    explored = set()
    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()[1]

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost,((new_x, new_y), frozenset(new_stones), new_path, new_cost, ),
                    )
                )

    return "No Solution"

def astar(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0)))
    explored = set()
    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()[1]

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost+calculate_heuristics(new_stones, new_x, new_y, switch_positions),
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                        ),
                    )
                )

    return "No Solution"

def gbfs(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0)))
    explored = set()
    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()[1]

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        calculate_heuristics(new_stones, new_x, new_y, switch_positions),
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                        ),
                    )
                )

    return "No Solution"

def weighted_astar(file_path):
    ares_position, stone_positions, switch_positions, index_wall = load_maze(file_path)
    start_time = time.time()
    trlloc.start()
    nodes_explored = 0
    frontier = q.PriorityQueue()
    frontier.put((0, (ares_position, frozenset(stone_positions), "", 0)))
    explored = set()
    while not frontier.empty():
        if (time.time() - start_time) >= OVERTIME:
            return "TimeOut"

        (ax, ay), stones, path, cost = frontier.get()[1]

        set_of_stones = set()
        for stone in stones:
            i, j, w = stone
            set_of_stones.add((i, j))

        if set_of_stones == switch_positions:
            end_time = time.time()
            _, memory = trlloc.get_traced_memory()
            trlloc.stop()
            step_not_push_stone = 0
            for c in path:
                if c.islower():
                    step_not_push_stone += 1
            return {
                "Step": len(path),
                "Weight": cost - step_not_push_stone,
                "Node": nodes_explored,
                "Path": path,
                "Time": "{:.2f}".format(1000 * (end_time - start_time)),
                "Memory": "{:.2f}".format(memory / (1024 * 1024)),
            }

        if (ax, ay, stones) in explored:
            continue
        explored.add((ax, ay, stones))
        nodes_explored = nodes_explored + 1

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
            new_path = path
            new_cost = cost

            stone_weight = 0
            if (new_x, new_y) in set_of_stones:
                (new_stone_x, new_stone_y) = (new_x + next_x, new_y + next_y)
                if (new_stone_x, new_stone_y) in index_wall or (
                    new_stone_x,
                    new_stone_y,
                ) in set_of_stones:
                    continue

                for stone in stones:
                    i, j, w = stone
                    if i == new_x and j == new_y:
                        stone_weight = w
                        break

                new_cost += stone_weight
                new_stones.add((new_stone_x, new_stone_y, stone_weight))
                new_stones.remove((new_x, new_y, stone_weight))
                move = move.upper()
            else:
                new_cost += 1
            new_path = new_path + move

            if not check_deadlock(set_of_stones, index_wall, switch_positions):
                frontier.put(
                    (
                        new_cost
                        + calculate_heuristics(
                            new_stones, new_x, new_y, switch_positions
                        )*weighted_astar_w,
                        (
                            (new_x, new_y),
                            frozenset(new_stones),
                            new_path,
                            new_cost,
                        ),
                    )
                )

    return "No Solution"

def write_result_to_output(level):
    level = int(level)
    path_input = (
        f"./input/input-0{level}.txt" if level < 10 else f"./input/input-{level}.txt"
    )
    path_output = (
        f"./output/output-0{level}.txt"
        if level < 10
        else f"./output/output-{level}.txt"
    )
    name_algo = ["BFS", "DFS", "UCS", "A*", "GBFS", "Weighted A*"]
    algo = [bfs, dfs, ucs, astar, gbfs, weighted_astar]
    file = open(path_output, "w")
    for i in range(len(algo)):
        file.write(f"{name_algo[i]}\n")
        result = algo[i](path_input)
        if result == "No Solution":
            file.write("No Solution\n")
        elif result == "TimeOut":
            file.write("Time Out\n")
        else:
            file.write(f"Step: {result['Step']}, ")
            file.write(f"Weight: {result['Weight']}, ")
            file.write(f"Node: {result['Node']}, ")
            file.write(f"Time: {result['Time']} ms, ")
            file.write(f"Memory: {result['Memory']} MB\n")
            file.write(f"{result['Path']}\n")
    file.close()
    print("Done!")
    print(f"Output file: {path_output}")

def write_result_to_output_for_list():
    start_level = 0
    end_level = 0
    for level in range(start_level, end_level + 1):
        level = int(level)
        path_input = (
            f"./input/input-0{level}.txt"
            if level < 10
            else f"./input/input-{level}.txt"
        )
        path_output = (
            f"./output/output-0{level}.txt"
            if level < 10
            else f"./output/output-{level}.txt"
        )
        name_algo = ["BFS", "DFS", "UCS", "A*", "GBFS", "Weighted A*"]
        algo = [bfs, dfs, ucs, astar, gbfs, weighted_astar]
        file = open(path_output, "w")
        for i in range(len(algo)):
            file.write(f"{name_algo[i]}\n")
            result = algo[i](path_input)
            if result == "No Solution":
                file.write("No Solution\n")
            elif result == "TimeOut":
                file.write("Time Out\n")
            else:
                file.write(f"Step: {result['Step']}, ")
                file.write(f"Weight: {result['Weight']}, ")
                file.write(f"Node: {result['Node']}, ")
                file.write(f"Time: {result['Time']} ms, ")
                file.write(f"Memory: {result['Memory']} MB\n")
                file.write(f"{result['Path']}\n")
        file.close()
        print("Done!")
        print(f"Output file: {path_output}")
