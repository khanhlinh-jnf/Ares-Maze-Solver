import copy

TIME_LIMITED = 1800
element_size = 50


class Game:

    def __init__(self):
        self.matrix = []
        self.width = self.height = 0
        self.step = 0
        self.stoneDict = {}
        self.weightList = []
        self.weight = 0


    def map_open(self, level):
        path = "./input/input-"

        if int(level) < 10:
            path = path + "0" + str(level) + ".txt"
        else:
            path = path + str(level) + ".txt"
        
        with open(path, "r") as file:
            lines = file.readlines()
            if lines:
                numLine = lines[0].strip()
                self.weightList.extend(map(int, numLine.split()))
                for line in lines[1:]: 
                    self.matrix.append(list(line))
        self.width, self.height = self.load_size()

    def GetStones(self):
        stones = []
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '$' or pos == '*':
                    stones.append((y, x))
                x += 1
            x = 0
            y += 1
        return stones

    def GetStonesDict(self):
        stones = self.GetStones()
        for stone, value in zip(stones, self.weightList):
            self.stoneDict[stone] = value
        return self.stoneDict


    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return ((x-1) * element_size, y * element_size)

    def reset(self, original_matrix):
        self.matrix = copy.deepcopy(original_matrix)
        self.step = 0
        self.weight = 0
        self.stoneDict = self.GetStonesDict()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_step(self):
        return self.step
    
    def get_weight(self):
        return self.weight

    def get_matrix(self):
        return self.matrix

    def print_map_test(self):
        for row in self.matrix:
            for char in row:
                print(char, end="")

    def valid_move(self, i, j, direction):

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
        Ares = (0, 0)
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] in ("@", "+"):
                    Ares = (i, j)
        moves = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        i, j = Ares
        if direction not in moves:
            return
        if not self.valid_move(i, j, direction):
            return
        dx, dy = moves[direction]
        new_x, new_y = i + dx, j + dy
        next_x, next_y = i + 2 * dx, j + 2 * dy

        current = self.matrix[new_x][new_y]

        if current in ("$", "*"):
            # Calculate the new weight
            self.weight += self.stoneDict.get((new_x, new_y))
            self.stoneDict[(next_x, next_y)] = self.stoneDict.pop((new_x, new_y))
            

            if self.matrix[next_x][next_y] in (" ", "."):
                self.matrix[next_x][next_y] = (
                    "*" if self.matrix[next_x][next_y] == "." else "$"
                )
            self.matrix[new_x][new_y] = "@" if current == "$" else "+"
        elif current == ".":
            self.matrix[new_x][new_y] = "+"
        else:
            self.matrix[new_x][new_y] = "@"
        self.matrix[i][j] = "." if self.matrix[i][j] == "+" else " "
        self.step += 1

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == "$":
                    return False
        return True
