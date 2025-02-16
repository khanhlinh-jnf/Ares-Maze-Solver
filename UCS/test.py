import queue
import copy
import time
import tracemalloc


class Stone:
    def __init__(self, weight, position):
        self.weight = weight
        self.position = position

    def __lt__(self, other):
        return self.weight < other.weight

    def set_weight(self, new_weight):
        self.weight = new_weight


class Maze:
    def __init__(self):
        self.real_and_heuristic = 0
        self.real_cost = 0
        self.heuristic = 0
        self.path_of_solution = ""
        self.matrix = []
        self.stones = []
        self.Ares = (0, 0)

    def __lt__(self, other):
        return self.real_and_heuristic < other.real_and_heuristic

    def add_stone(self, stone):
        self.stones.append(stone)

    def load_maze(self, file_name):
        matrix = []
        weight_of_stones = []
        with open(file_name) as f:
            weight_of_stones = list(map(int, f.readline().strip().split()))
            for line in f:
                row = []
                for char in line:
                    if char != "\n" and char in [" ", "#", "@", "+", "$", "*", "."]:
                        if char in ["@", "+"]:
                            self.Ares = (len(matrix), len(row))
                        if char in ["$", "*"]:
                            self.add_stone(
                                Stone(weight_of_stones.pop(0), (len(matrix), len(row)))
                            )
                        row.append(char)
                matrix.append(row)
        self.matrix = matrix

    def show_info(self):
        print("Ares: ", self.Ares)
        print("Stones: ")
        self.show_stones()

    def show_stones(self):
        for stone in self.stones:
            print(stone.weight, stone.position)

    def get_matrix(self):
        return str(self.matrix)

    def print_map(self):
        for row in self.matrix:
            for char in row:
                print(char, end="")
            print()

    def goal_state(self):
        for row in self.matrix:
            for char in row:
                if char == "$":
                    return False
        return True

    def find_list_of_switches(self):
        switches = []
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] in [".", "*", "+"]:
                    switches.append((i, j))
        return switches

    def valid_move(self, direction):
        i, j = self.Ares
        moves = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

        if direction not in moves:
            return False

        dx, dy = moves[direction]
        new_x, new_y = i + dx, j + dy
        next_x, next_y = i + 2 * dx, j + 2 * dy

        if self.matrix[new_x][new_y] in ("$", "*"):
            return self.matrix[next_x][next_y] in (" ", ".")

        return self.matrix[new_x][new_y] in (" ", ".")

    def Ares_move(self, direction):
        direction_custom = direction.lower()
        cost = 1
        moves = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        i, j = self.Ares

        dx, dy = moves[direction]
        new_x, new_y = i + dx, j + dy
        next_x, next_y = i + 2 * dx, j + 2 * dy

        current = self.matrix[new_x][new_y]

        if current in ("$", "*"):
            if self.matrix[next_x][next_y] in (" ", "."):
                self.matrix[next_x][next_y] = (
                    "*" if self.matrix[next_x][next_y] == "." else "$"
                )

                for stone in self.stones:
                    if stone.position == (new_x, new_y):
                        stone.position = (next_x, next_y)
                        cost = stone.weight
                        direction_custom = direction_custom.upper()
            self.matrix[new_x][new_y] = "@" if current == "$" else "+"
        elif current == ".":
            self.matrix[new_x][new_y] = "+"
        else:
            self.matrix[new_x][new_y] = "@"

        self.matrix[i][j] = "." if self.matrix[i][j] == "+" else " "
        self.Ares = (new_x, new_y)
        return direction_custom, cost

    def is_deadlock(self):
        for stone in self.stones:
            i, j = stone.position
            if self.matrix[i][j] == "*": continue
            # left - up corner
            if self.matrix[i - 1][j] in ["#", "$", "*"] and self.matrix[i][j - 1] in [
                "#",
                "$",
                "*",
            ]:
                if self.matrix[i - 1][j - 1] in ["#", "$", "*"]:
                    return True
                if self.matrix[i - 1][j] == "#" and self.matrix[i][j - 1] == "#":
                    return True
                if self.matrix[i - 1][j] in ["$", "*"] and self.matrix[i][j - 1] in [
                    "$",
                    "*",
                ]:
                    if (
                        self.matrix[i + 1][j - 1] == "#"
                        and self.matrix[i - 1][j + 1] == "#"
                    ):
                        return True
                if self.matrix[i][j - 1] in ["$", "*"] and self.matrix[i - 1][j] == "#":
                    if self.matrix[i + 1][j - 1] == "#":
                        return True
                if self.matrix[i][j - 1] == "#" and self.matrix[i - 1][j] in ["$", "*"]:
                    if self.matrix[i - 1][j + 1] == "#":
                        return True
            # right - down corner
            if self.matrix[i + 1][j] in ["#", "$", "*"] and self.matrix[i][j + 1] in [
                "#",
                "$",
                "*",
            ]:
                if self.matrix[i + 1][j + 1] in ["#", "$", "*"]:
                    return True
                if self.matrix[i + 1][j] == "#" and self.matrix[i][j + 1] == "#":
                    return True
                if self.matrix[i + 1][j] in ["$", "*"] and self.matrix[i][j + 1] in [
                    "$",
                    "*",
                ]:
                    if (
                        self.matrix[i - 1][j + 1] == "#"
                        and self.matrix[i + 1][j - 1] == "#"
                    ):
                        return True
                if self.matrix[i][j + 1] in ["$", "*"] and self.matrix[i + 1][j] == "#":
                    if self.matrix[i - 1][j + 1] == "#":
                        return True
                if self.matrix[i][j + 1] == "#" and self.matrix[i + 1][j] in ["$", "*"]:
                    if self.matrix[i + 1][j - 1] == "#":
                        return True
            # left - down corner
            if self.matrix[i + 1][j] in ["#", "$", "*"] and self.matrix[i][j - 1] in [
                "#",
                "$",
                "*",
            ]:
                if self.matrix[i + 1][j - 1] in ["#", "$", "*"]:
                    return True
                if self.matrix[i + 1][j] == "#" and self.matrix[i][j - 1] == "#":
                    return True
                if self.matrix[i + 1][j] in ["$", "*"] and self.matrix[i][j - 1] in [
                    "$",
                    "*",
                ]:
                    if (
                        self.matrix[i - 1][j - 1] == "#"
                        and self.matrix[i + 1][j + 1] == "#"
                    ):
                        return True
                if self.matrix[i][j - 1] in ["$", "*"] and self.matrix[i + 1][j] == "#":
                    if self.matrix[i - 1][j - 1] == "#":
                        return True
                if self.matrix[i][j - 1] == "#" and self.matrix[i + 1][j] in ["$", "*"]:
                    if self.matrix[i + 1][j + 1] == "#":
                        return True
            # right - up corner
            if self.matrix[i - 1][j] in ["#", "$", "*"] and self.matrix[i][j + 1] in [
                "#",
                "$",
                "*",
            ]:
                if self.matrix[i - 1][j + 1] in ["#", "$", "*"]:
                    return True
                if self.matrix[i - 1][j] == "#" and self.matrix[i][j + 1] == "#":
                    return True
                if self.matrix[i - 1][j] in ["$", "*"] and self.matrix[i][j + 1] in [
                    "$",
                    "*",
                ]:
                    if (
                        self.matrix[i + 1][j + 1] == "#"
                        and self.matrix[i - 1][j - 1] == "#"
                    ):
                        return True
                if self.matrix[i][j + 1] in ["$", "*"] and self.matrix[i - 1][j] == "#":
                    if self.matrix[i + 1][j + 1] == "#":
                        return True
                if self.matrix[i][j + 1] == "#" and self.matrix[i - 1][j] in ["$", "*"]:
                    if self.matrix[i - 1][j - 1] == "#":
                        return True
            return False


def Ares_to_switch(maze):
    cost = 1000
    list_of_switches = maze.find_list_of_switches()
    for stone in maze.stones:
        for switch in list_of_switches:
            res = abs(stone.position[0] - switch[0]) + abs(
                stone.position[1] - switch[1]
            )
            if res < cost:
                cost = res
    return cost


def compute_cost_to_goal(maze):
    total = 0
    list_of_switches = maze.find_list_of_switches()
    for stone in maze.stones:
        cost = 0
        for switch in list_of_switches:
            cost += abs(stone.position[0] - switch[0]) + abs(
                stone.position[1] - switch[1]
            )
        total += cost * stone.weight
    return total


def compute_heuristic(maze):
    total_cost = 0
    list_of_switches = maze.find_list_of_switches()
    p_queue = queue.PriorityQueue()
    for stone in maze.stones:
        stone.set_weight(-stone.weight)
        p_queue.put(stone)
    used = []
    while not p_queue.empty():
        stone = p_queue.get()
        stone.set_weight(-stone.weight)
        cost = 1e9
        match = (0, 0)
        for switch in list_of_switches:
            if switch in used:
                continue
            res = abs(stone.position[0] - switch[0]) + abs(
                stone.position[1] - switch[1]
            )
            if res < cost:
                cost = res
                match = switch
        used.append(match)
        total_cost += cost * stone.weight
    return total_cost


def astar_search(maze):
    print("A*")
    start_time = time.time()
    
    if maze.is_deadlock():
        end_time = time.time()
        str_node = "Node: 0"
        str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
        return str_node + str_time + "\n" + "No solution"

    start = copy.deepcopy(maze)
    frontier = queue.PriorityQueue()
    frontier.put(start)
    explored = []
    node = 1

    while not frontier.empty():
        print(node, end="\r")
        current = frontier.get()
        explored.append(str(current.get_matrix()))

        if current.goal_state():
            print("Complete..........")
            end_time = time.time()
            str_step = "Steps: " + str(len(current.path_of_solution))
            str_cost = "Weight: " + str(current.real_cost)
            str_node = "Node: " + str(node)
            str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
            return (
                str_step
                + ", "
                + str_cost
                + ", "
                + str_node
                + ", "
                + str_time
                + "\n"
                + current.path_of_solution
            )

        valid_moves = []
        for direction in ["U", "D", "L", "R"]:
            if current.valid_move(direction):
                valid_moves.append(direction)

        for direction in valid_moves:
            new_maze = copy.deepcopy(current)
            direction_custom, cost = new_maze.Ares_move(direction)
            new_maze.real_cost += cost
            new_maze.heuristic = compute_heuristic(new_maze)
            new_maze.real_and_heuristic = new_maze.heuristic + new_maze.real_cost
            new_maze.path_of_solution += direction_custom
            if new_maze.get_matrix() not in explored and not new_maze.is_deadlock():
                frontier.put(new_maze)
                node += 1

    print("Complete..........")
    end_time = time.time()
    str_node = "Node: " + str(node)
    str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
    return str_node + str_time + "\n" + "No solution"


def gbfs_search(maze):
    print("GBFS")
    start_time = time.time()
    
    if maze.is_deadlock():
        end_time = time.time()
        str_node = "Node: 0"
        str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
        return str_node + str_time + "\n" + "No solution"

    start = copy.deepcopy(maze)
    frontier = queue.PriorityQueue()
    frontier.put(start)
    explored = []
    node = 1

    while not frontier.empty():
        print(node, end="\r")
        current = frontier.get()
        explored.append(str(current.get_matrix()))

        if current.goal_state():
            print("Complete..........")
            end_time = time.time()
            str_step = "Steps: " + str(len(current.path_of_solution))
            str_cost = "Weight: " + str(current.real_cost)
            str_node = "Node: " + str(node)
            str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
            return (
                str_step
                + ", "
                + str_cost
                + ", "
                + str_node
                + ", "
                + str_time
                + "\n"
                + current.path_of_solution
            )

        valid_moves = []
        for direction in ["U", "D", "L", "R"]:
            if current.valid_move(direction):
                valid_moves.append(direction)

        for direction in valid_moves:
            new_maze = copy.deepcopy(current)
            direction_custom, cost = new_maze.Ares_move(direction)
            new_maze.real_cost += cost
            new_maze.heuristic = compute_heuristic(new_maze)
            new_maze.real_and_heuristic = new_maze.heuristic
            new_maze.path_of_solution += direction_custom
            if new_maze.get_matrix() not in explored and not new_maze.is_deadlock():
                frontier.put(new_maze)
                node += 1

    print("Complete..........")
    end_time = time.time()
    str_node = "Node: " + str(node)
    str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
    return str_node + str_time + "\n" + "No solution"


def ucs_search(maze):
    print("UCS")
    start_time = time.time()
    
    if maze.is_deadlock():
        end_time = time.time()
        str_node = "Node: 0"
        str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
        return str_node + str_time + "\n" + "No solution"

    start = copy.deepcopy(maze)
    frontier = queue.PriorityQueue()
    frontier.put(start)
    explored = []
    node = 1

    while not frontier.empty():
        # print(node, end="\r")
        current = frontier.get()
        explored.append(str(current.get_matrix()))

        if current.goal_state():
            print("Complete..........")
            end_time = time.time()
            str_step = "Steps: " + str(len(current.path_of_solution))
            str_cost = "Weight: " + str(current.real_cost)
            str_node = "Node: " + str(node)
            str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
            return (
                str_step
                + ", "
                + str_cost
                + ", "
                + str_node
                + ", "
                + str_time
                + "\n"
                + current.path_of_solution
            )

        valid_moves = []
        for direction in ["U", "D", "L", "R"]:
            if current.valid_move(direction):
                valid_moves.append(direction)

        for direction in valid_moves:
            new_maze = copy.deepcopy(current)
            direction_custom, cost = new_maze.Ares_move(direction)
            new_maze.real_cost += cost
            new_maze.heuristic = 0
            new_maze.real_and_heuristic = new_maze.real_cost + new_maze.heuristic
            new_maze.path_of_solution += direction_custom
            if new_maze.get_matrix() not in explored and not new_maze.is_deadlock():
                frontier.put(new_maze)
                node += 1

    print("Complete..........")
    end_time = time.time()
    str_node = "Node: " + str(node)
    str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
    return str_node + str_time + "\n" + "No solution"


def bfs_search(maze):
    print("BFS")
    start_time = time.time()
    
    if maze.is_deadlock():
        end_time = time.time()
        str_node = "Node: 0"
        str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
        return str_node + str_time + "\n" + "No solution"

    start = copy.deepcopy(maze)
    frontier = queue.Queue()
    frontier.put(start)
    explored = []
    node = 1

    while not frontier.empty():
        print(node, end="\r")
        current = frontier.get()
        explored.append(str(current.get_matrix()))

        if current.goal_state():
            print("Complete..........")
            end_time = time.time()
            str_step = "Steps: " + str(len(current.path_of_solution))
            str_cost = "Weight: " + str(current.real_cost)
            str_node = "Node: " + str(node)
            str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
            return (
                str_step
                + ", "
                + str_cost
                + ", "
                + str_node
                + ", "
                + str_time
                + "\n"
                + current.path_of_solution
            )

        valid_moves = []
        for direction in ["U", "D", "L", "R"]:
            if current.valid_move(direction):
                valid_moves.append(direction)

        for direction in valid_moves:
            new_maze = copy.deepcopy(current)
            direction_custom, cost = new_maze.Ares_move(direction)
            new_maze.real_cost += cost
            new_maze.path_of_solution += direction_custom
            if new_maze.goal_state():
                print("Complete..........")
                end_time = time.time()
                str_step = "Steps: " + str(len(new_maze.path_of_solution))
                str_cost = "Weight: " + str(new_maze.real_cost)
                str_node = "Node: " + str(node)
                str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
                return (
                    str_step
                    + ", "
                    + str_cost
                    + ", "
                    + str_node
                    + ", "
                    + str_time
                    + "\n"
                    + new_maze.path_of_solution
                )
            if new_maze.get_matrix() not in explored and not new_maze.is_deadlock():
                frontier.put(new_maze)
                node += 1

    print("Complete..........")
    end_time = time.time()
    str_node = "Node: " + str(node)
    str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
    return str_node + str_time + "\n" + "No solution"


def dfs_search(maze):
    print("DFS")
    start_time = time.time()

    if maze.is_deadlock():
        end_time = time.time()
        str_node = "Node: 0"
        str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
        return str_node + str_time + "\n" + "No solution"

    start = copy.deepcopy(maze)
    frontier = queue.LifoQueue()
    frontier.put(start)
    explored = []
    node = 1

    while not frontier.empty():
        print(node, end="\r")
        current = frontier.get()
        explored.append(str(current.get_matrix()))

        if current.goal_state():
            print("Complete..........")
            end_time = time.time()
            str_step = "Steps: " + str(len(current.path_of_solution))
            str_cost = "Weight: " + str(current.real_cost)
            str_node = "Node: " + str(node)
            str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
            return (
                str_step
                + ", "
                + str_cost
                + ", "
                + str_node
                + ", "
                + str_time
                + "\n"
                + current.path_of_solution
            )

        valid_moves = []
        for direction in ["U", "D", "L", "R"]:
            if current.valid_move(direction):
                valid_moves.append(direction)

        for direction in valid_moves:
            new_maze = copy.deepcopy(current)
            direction_custom, cost = new_maze.Ares_move(direction)
            new_maze.real_cost += cost
            new_maze.path_of_solution += direction_custom
            if new_maze.goal_state():
                print("Complete..........")
                end_time = time.time()
                str_step = "Steps: " + str(len(new_maze.path_of_solution))
                str_cost = "Weight: " + str(new_maze.real_cost)
                str_node = "Node: " + str(node)
                str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
                return (
                    str_step
                    + ", "
                    + str_cost
                    + ", "
                    + str_node
                    + ", "
                    + str_time
                    + "\n"
                    + new_maze.path_of_solution
                )
            if new_maze.get_matrix() not in explored and not new_maze.is_deadlock():
                frontier.put(new_maze)
                node += 1

    print("Complete..........")
    end_time = time.time()
    str_node = "Node: " + str(node)
    str_time = "Time (ms): " + str(round((end_time - start_time) * 1000, 2))
    return str_node + str_time + "\n" + "No solution"

for n in range(6, 7):
    print("\nTest case: ", n)
    game = Maze()
    file_in = "input-0" + str(n) + ".txt" if int(n) < 10 else "input-" + str(n) + ".txt"
    game.load_maze("input\\"+file_in)
    print("UCS")
    print(ucs_search(copy.deepcopy(game)))

# game = Maze()
# game.load_maze("sokoban_input\\input-04.txt")
# print(bfs_search(copy.deepcopy(game)))

# game = Maze()
# game.load_maze("sokoban_input\\input-06.txt")
# str = "luRuUruRldlddRRdrruLLLrruuruulDDDuulldlluRRRldldDlddrUUUdrrdrruLLLrruuruulDlllldRdDlddrUUUdrrruUruL"
# cost = 0
# count = 0
# for i in str:
#     cost += game.Ares_move(i.upper())[1]
# print("Steps: ", len(str))
# print("Cost: ", cost)
# game.print_map()
# if game.is_deadlock():
#     print("Deadlock")
# Beta
# 0 / 0
# used queries


# 1