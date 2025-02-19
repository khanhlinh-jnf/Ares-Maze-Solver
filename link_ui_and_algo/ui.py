import sys
import pygame
import time
import sokoban

TIME_LIMITED = 1800


class Game:
    def __init__(self, matrix):
        self.matrix = matrix

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

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

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == "$":
                    return False
        return True


def load_maze(level):
    path = (
        "input/input-0" + str(level) + ".txt"
        if int(level) < 10
        else "input/input-" + str(level) + ".txt"
    )
    matrix = []
    weight_of_stones = []
    with open(path) as f:
        weight_of_stones = list(map(int, f.readline().strip().split()))
        for line in f:
            row = []
            for char in line:
                if char != "\n" and char in [" ", "#", "@", "+", "$", "*", "."]:
                    row.append(char)
            matrix.append(row)
    return matrix


def playByBot(game, move):
    move = move.upper()
    if move == "U":
        game.Ares_move("U")
    elif move == "D":
        game.Ares_move("D")
    elif move == "L":
        game.Ares_move("L")
    elif move == "R":
        game.Ares_move("R")


def print_game(matrix, screen):
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == " ":  # floor
                screen.blit(floor, (x, y))
            elif char == "#":  # wall
                screen.blit(wall, (x, y))
            elif char == "@":  # worker on floor
                screen.blit(worker, (x, y))
            elif char == ".":  # dock
                screen.blit(docker, (x, y))
            elif char == "*":  # box on dock
                screen.blit(box_docked, (x, y))
            elif char == "$":  # box
                screen.blit(box, (x, y))
            elif char == "+":  # worker on dock
                screen.blit(worker_docked, (x, y))
            x = x + 32
        x = 0
        y = y + 32


def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            return event.key
        else:
            pass


def display_box(screen, message):
    "Print a message in a box in the middle of the screen"
    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10, 200, 20),
        0,
    )
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        ((screen.get_width() / 2) - 102, (screen.get_height() / 2) - 12, 204, 24),
        1,
    )
    if len(message) != 0:
        screen.blit(
            fontobject.render(message, 1, (255, 255, 255)),
            ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10),
        )
    pygame.display.flip()


def display_end(screen, msg):
    if msg == "Done":
        message = "Level Completed"
    elif msg == "Cannot":
        message = "No Solution"
    elif msg == "Out":
        message = "Time Out! Cannot find solution"
    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10, 200, 20),
        0,
    )
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        ((screen.get_width() / 2) - 102, (screen.get_height() / 2) - 12, 204, 24),
        1,
    )
    screen.blit(
        fontobject.render(message, 1, (255, 255, 255)),
        ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10),
    )
    pygame.display.flip()


def ask(screen, question):
    "ask(screen, question) -> answer"
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + "".join(current_string))
    while 1:
        inkey = get_key()
        if inkey == pygame.K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == pygame.K_RETURN:
            break
        elif inkey == pygame.K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + "".join(current_string))
    return "".join(current_string)


def start_game():
    start = pygame.display.set_mode((320, 240))
    level = ask(start, "Select Level")
    if int(level) > 0:
        return level
    else:
        print("ERROR: Invalid Level: " + str(level))
        sys.exit(2)


wall = pygame.image.load(".\images\wall.png")
floor = pygame.image.load(".\images/floor.png")
box = pygame.image.load(".\images/box.png")
box_docked = pygame.image.load(".\images/box_docked.png")
worker = pygame.image.load(".\images\worker.png")
worker_docked = pygame.image.load(".\images\worker_dock.png")
docker = pygame.image.load(".\images\dock.png")
background = 255, 226, 191
pygame.init()


level = start_game()
game = Game(load_maze(level))
path = "input/input-0" + str(level) + ".txt" if int(level) < 10 else "input/input-" + str(level) + ".txt"
size = game.load_size()
screen = pygame.display.set_mode(size)
sol = ""
# sol = BFSsolution(game)
# sol = AstarSolution(game)
i = 0
flagAuto = 0
while 1:
    print_game(game.get_matrix(), screen)

    if sol == "NoSol":
        display_end(screen, "Cannot")
    if sol == "TimeOut":
        display_end(screen, "Out")
    if game.is_completed():
        display_end(screen, "Done")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit(0)
            elif event.key == pygame.K_b:
                print("BFS is running")
                flagAuto = 1
                res = sokoban.bfs(path)
                print(res)
                sol = res["Path: "]
            elif event.key == pygame.K_a:
                print("A* is running")
                flagAuto = 1
                res = sokoban.astar(path)
                print(res)
                sol = res["Path: "]
            elif event.key == pygame.K_d:
                print("DFS is running")
                flagAuto = 1
                res = sokoban.dfs(path)
                print(res)
                sol = res["Path: "]
            elif event.key == pygame.K_g:
                print("GBFS is running")
                flagAuto = 1
                res = sokoban.gbfs(path)
                print(res)
                sol = res["Path: "]
            elif event.key == pygame.K_u:
                print("UCS is running")
                flagAuto = 1
                res = sokoban.ucs(path)
                print(res)
                sol = res["Path: "]
                
    if (flagAuto) and (i < len(sol)):
        playByBot(game, sol[i])
        i += 1
        if i == len(sol):
            flagAuto = 0
        time.sleep(0.1)

    pygame.display.update()
