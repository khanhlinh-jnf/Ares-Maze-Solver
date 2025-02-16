import heapq
import time
import psutil

def ReadInput(InputPath):
    """ Reads the input file and extracts stone weights and the grid. """
    with open(InputPath, "r") as f:
        lines = f.readlines()

    stone_weights = list(map(int, lines[0].strip().split()))  # Convert weights to a list of integers
    grid = [list(line.rstrip()) for line in lines[1:]]  # Convert grid to 2D list
    return stone_weights, grid

def GetPositions(grid):
    """ Extracts positions of Ares, stones, and switches from the grid. """
    positions = {"Ares": None, "Stones": [], "Switches": []}
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == "@":
                positions["Ares"] = (r, c)
            elif cell == "$":
                positions["Stones"].append((r, c))
            elif cell == ".":
                positions["Switches"].append((r, c))
            elif cell == "*":
                positions["Stones"].append((r, c))
                positions["Switches"].append((r, c))
            elif cell == "+":
                positions["Ares"] = (r, c)
                positions["Switches"].append((r, c))
    return positions

def validMove(grid, r, c):
    """ Checks if a position is within bounds and not a wall. """
    return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] != "#"

def FindPath(stone_weights, grid):
    """ Implements Uniform Cost Search (UCS) to find the optimal path. """
    positions = GetPositions(grid)
    start = positions["Ares"]
    goal = set(positions["Switches"])
    nodeExpand = 0

    # Stones are stored as ((row, col), weight) tuples
    stones_list = []  # Create an empty list for storing stone data
    for i in range(len(positions["Stones"])):
        stone_position = positions["Stones"][i]  # Get stone position
        stone_weight = stone_weights[i]  # Get corresponding stone weight
        stones_list.append((stone_position, stone_weight))  # Store as tuple

    stones = tuple(stones_list)  # Convert list to tuple (immutable)


    pq = [(0, start, stones, "")]  # Priority queue: (cost, Ares_pos, Stones_pos, path)
    visited = set()
    directions = [(0, -1, 'l'), (0, 1, 'r'), (-1, 0, 'u'), (1, 0, 'd')]

    while pq:
        cost, ares_pos, stones_pos, path = heapq.heappop(pq)
        nodeExpand += 1

        # Goal check: all stones should be on switches
        if all(stone[0] in goal for stone in stones_pos):
            return cost, path, nodeExpand  # Return optimal cost and path

        if (ares_pos, stones_pos) in visited:  
            continue
        visited.add((ares_pos, stones_pos))

        for dr, dc, move in directions:
            new_r, new_c = ares_pos[0] + dr, ares_pos[1] + dc

            if not validMove(grid, new_r, new_c):  
                continue

            new_stones = list(stones_pos)  

            for i, (stone_pos, weight) in enumerate(new_stones):
                if stone_pos == (new_r, new_c):  # Ares is pushing a stone
                    push_pos = (stone_pos[0] + dr, stone_pos[1] + dc)

                    # Ensure the stone can be pushed
                    if not validMove(grid, push_pos[0], push_pos[1]) or push_pos in [s[0] for s in new_stones]:
                        break

                    # Update stone's position
                    new_stones[i] = (push_pos, weight)
                    new_cost = cost + weight  # Add weight to the movement cost
                    move = move.upper()  # Convert move to uppercase (stone push)
                else:
                    new_cost = cost + 1  # Regular move cost

            else:
                heapq.heappush(pq, (new_cost, (new_r, new_c), tuple(new_stones), path + move))

    return -1, "", nodeExpand  # No solution found

def SaveOutput(OutputPath, cost, path, nodeExpand, elapsedTime, memoryUsed):
    """ Saves the result to an output file. """
    with open(OutputPath, "w") as f:
        if cost == -1:
            f.write("No solution found\n")
        else:
            f.write(f"UCS\nSteps: {len(path)}, Weight: {cost}, Node: {nodeExpand}, Time (ms): {elapsedTime * 1000}, Memory (MB): {memoryUsed}\n")
            f.write(f"{path}\n")

def FillPositions(grid, ares_pos, stones_pos, switches_pos):
    for idx in switches_pos:
        grid[idx[0]][idx[1]] = "."
    for idx in stones_pos:
        if idx in switches_pos:
            grid[idx[0]][idx[1]] = "*"
        else:
            grid[idx[0]][idx[1]] = "$"
    if ares_pos in switches_pos:
        grid[ares_pos[0]][ares_pos[1]] = "+"
    else:
        grid[ares_pos[0]][ares_pos[1]] = "@"

def DisplayGrid(grid):
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            print(cell, end="")
        print()

def ResetGrid(grid):
    gridLayout = grid
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == "#":
                gridLayout[r][c] = "#"
            else:
                gridLayout[r][c] = " "

    return gridLayout

def ShowPath(path, grid):
    positions = GetPositions(grid)
    ares_pos = positions["Ares"]
    stones = positions["Stones"]
    switches = positions["Switches"]
    step = 1
    gridLayout = ResetGrid(grid)
    
    print(f"step: 0")
    FillPositions(gridLayout, ares_pos, stones, switches)
    DisplayGrid(gridLayout)
    gridLayout = ResetGrid(grid)

    for move in path:
        print(f"step: {step}")
        step += 1
        if move == "l" or move == "L":
            ares_pos = (ares_pos[0], ares_pos[1] - 1)
            if ares_pos in stones:
                idx = stones.index(ares_pos)
                stones[idx] = (ares_pos[0], ares_pos[1] - 1)
            FillPositions(gridLayout, ares_pos, stones, switches)
            DisplayGrid(gridLayout)
            gridLayout = ResetGrid(grid)
        elif move == "r" or move == "R":
            ares_pos = (ares_pos[0], ares_pos[1] + 1)
            if ares_pos in stones:
                idx = stones.index(ares_pos)
                stones[idx] = (ares_pos[0], ares_pos[1] + 1)
            FillPositions(gridLayout, ares_pos, stones, switches)
            DisplayGrid(gridLayout)
            gridLayout = ResetGrid(grid)
        elif move == "u" or move == "U":
            ares_pos = (ares_pos[0] - 1, ares_pos[1])
            if ares_pos in stones:
                idx = stones.index(ares_pos)
                stones[idx] = (ares_pos[0] - 1, ares_pos[1])
            FillPositions(gridLayout, ares_pos, stones, switches)
            DisplayGrid(gridLayout)
            gridLayout = ResetGrid(grid)
        elif move == "d" or move == "D":
            ares_pos = (ares_pos[0] + 1, ares_pos[1])
            if ares_pos in stones:
                idx = stones.index(ares_pos)
                stones[idx] = (ares_pos[0] + 1, ares_pos[1])
            FillPositions(gridLayout, ares_pos, stones, switches)
            DisplayGrid(gridLayout)
            gridLayout = ResetGrid(grid)


if __name__ == "__main__":
    input_path = "input/input-01.txt"
    output_path = "output/output-01.txt"
    level = int(input("Enter level (1->10): "))

    if level < 1:
        print("Invalid level")
        exit()
    
    if level < 10:
        input_path = f"input/input-0{level}.txt"
        output_path = f"output/output-0{level}.txt"
    else:
        input_path = f"input/input-{level}.txt"
        output_path = f"output/output-{level}.txt"

    stone_weights, grid = ReadInput(input_path)

    start_time = time.time()
    process = psutil.Process() # Get current process
    memory_before = process.memory_info().rss / (1024 * 1024)

    cost, path, nodeExpand = FindPath(stone_weights, grid)

    end_time = time.time()
    memory_after = process.memory_info().rss / (1024 * 1024) # Memory usage in MB

    elapsed_time = round(end_time - start_time, 2)
    memory_used = round(memory_after - memory_before, 2)

    SaveOutput(output_path, cost, path, nodeExpand, elapsed_time, memory_used)
    ShowPath(path, grid)
    
