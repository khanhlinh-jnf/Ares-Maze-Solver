import sys
import pygame

element_size = 50
wall = pygame.image.load("assets\\resources\wall.png")
space = pygame.image.load("assets\\resources/space.png")
stone = pygame.image.load("assets\\resources/stone.png")
stone_docked = pygame.image.load("assets\\resources/stone_docked.png")
player = pygame.image.load("assets\\resources\player.png")
player_docked = pygame.image.load("assets\\resources\player_docked.png")
switch = pygame.image.load("assets\\resources\switch.png")
background = 240, 210, 225


# def CheckValidLevel(level):
#     for i in level:
#         if i 

def GetKey():
    while 1:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            return event.key
        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
        else:
            pass

def DisplayBox(screen, message, firstLogin):
  fontobject = pygame.font.SysFont("timesnewroman",18)
  pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
  pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    if not firstLogin:
        screen.blit(fontobject.render("Enter valid number", 1, (255,255,255)),
            ((screen.get_width() / 2) - 100, (screen.get_height() / 2) + 10))
  pygame.display.flip()

def ask(screen, firstLogin):
  question = "Select level"
  pygame.font.init()
  current_string = []
  DisplayBox(screen, question + ": " + "".join(current_string), firstLogin)
  while 1:
    inkey = GetKey()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    DisplayBox(screen, question + ": " + "".join(current_string), firstLogin)
  return "".join(current_string)

def CheckValidNumber(str):
    for i in str:
        if i < "0" or i > "9":
            return False
    if int(str) > 17:
        return False
    return True

def StartGame(firstLogin):
    start = pygame.display.set_mode((320,240))
    level = ask(start, firstLogin)
    if CheckValidNumber(level):
        return level, True
    return -1, False


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


def print_game(matrix, screen, header_height):
    screen.fill(background)
    x = 0
    y = header_height
    for row in matrix:
        for char in row:
            if char == " ": 
                screen.blit(space, (x, y))
            elif char == "#":  
                screen.blit(wall, (x, y))
            elif char == "@":  
                screen.blit(player, (x, y))
            elif char == ".":  
                screen.blit(switch, (x, y))
            elif char == "*":  
                screen.blit(stone_docked, (x, y))
            elif char == "$":  
                screen.blit(stone, (x, y))
            elif char == "+":  
                screen.blit(player_docked, (x, y))
            x = x + element_size
        x = 0
        y = y + element_size


def display_information(screen, msg):
    if msg == "Done":
        message = "Level Completed! Press q or r"
    elif msg == "Cannot":
        message = "No Solution"
    elif msg == "Out":
        message = "Time Out! Cannot find solution"
    elif msg == "BFS":
        message = "BFS is running"
    elif msg == "DFS":
        message = "DFS is running"
    elif msg == "UCS":
        message = "UCS is running"
    elif msg == "A*":
        message = "A* is running"
    elif msg == "GBFS":
        message = "GBFS is running"
    elif msg == "Swarm":
        message = "Swarm is running"
    elif msg == "Output":
        message = "Writing result to file at folder"

    fontobject = pygame.font.SysFont("timesnewroman", 14)
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

pygame.font.init()
font = pygame.font.SysFont("timesnewroman", 14)  # Chọn font mặc định, kích thước 36

def display_header(width, height, screen, step, weight):
    header = pygame.Surface((width, height))
    header.fill((255, 255, 255))
    msg = "Step: " + str(step) + "                Weight: " + str(weight)
    text_surface = font.render(msg, True, (0, 0, 0))
    screen.blit(header, (0, 0))
    screen.blit(text_surface, (20, 5))


def display_header_final(width, height, screen, output):
    header = pygame.Surface((width, height))
    header.fill((255, 255, 255))
    msg = [
        "Statistics:",
        "  Step: "
        + str(output["Step"])
        + "                Weight: "
        + str(output["Weight"])
        + "                Node: "
        + str(output["Node"]),
        "  Time: "
        + str(output["Time"])
        + " ms"
        + "                           Memory: "
        + str(output["Memory"])
        + " MB",
    ]
    screen.blit(header, (0, 0))
    for i, line in enumerate(msg):
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (20, i * 20))


def display_footer(width, offset, footer_height, screen):
    footer = pygame.Surface((width, footer_height))
    footer.fill((255, 255, 255))

    options = [
        "Choose algorithm:                         Intruction:",
        "[1] BFS   [2] DFS     [3] UCS        [q] quit  [o] get output  [r] reset",
        "[4] A*     [5] GBFS   [6] Swarm     [p] pause/continue aminimation",
    ]

    # Render text
    screen.blit(footer, (0, offset))

    for i, line in enumerate(options):
        text_surface = font.render(line, True, (0, 0, 0))  # Black text
        screen.blit(text_surface, (5, offset + 5 + (i * 20)))
