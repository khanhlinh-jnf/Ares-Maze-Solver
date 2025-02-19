import sys
import pygame
import string
import queue
import copy
import time

TIME_LIMITED = 1800

element_size = 64
wall = pygame.image.load('assets\\resources\wall.png')
space = pygame.image.load('assets\\resources/space.png')
stone = pygame.image.load('assets\\resources/stone.png')
stone_docked = pygame.image.load('assets\\resources/stone_docked.png')
player = pygame.image.load('assets\\resources\player.png')
player_docked = pygame.image.load('assets\\resources\player_docked.png')
switch = pygame.image.load('assets\\resources\switch.png')
background = 255, 204, 229

def playByBot(game,move):
    if move == "U":
        game.move(0,-1,False)
    elif move == "D":
        game.move(0,1,False)
    elif move == "L":
        game.move(-1,0,False)
    elif move == "R":
        game.move(1,0,False)
    else:
        game.move(0,0,False)

def map_open(level):
    path = "./assets/input/input-"
    matrix = []

    if int(level) < 10:
        path = path + "0" + str(level) + ".txt"
    else:
        path = path + str(level) + ".txt"
    
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            matrix.append(list(line))

    return matrix
            
#   
    
def print_game(matrix,screen):
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ': #floor
                screen.blit(space,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '@': #worker on floor
                screen.blit(player,(x,y))
            elif char == '.': #dock
                screen.blit(switch,(x,y))
            elif char == '*': #box on dock
                screen.blit(stone_docked,(x,y))
            elif char == '$': #box
                screen.blit(stone,(x,y))
            elif char == '+': #worker on dock
                screen.blit(player_docked,(x,y))
            x = x + element_size
        x = 0
        y = y + element_size

def display_end(screen,msg):
    if msg == "Done":
        message = "Level Completed"
    elif msg == "Cannot":
        message = "No Solution"
    elif msg == "Out":
        message = "Time Out! Cannot find solution"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()

pygame.font.init()
font = pygame.font.Font(None, 16)  # Chọn font mặc định, kích thước 36


def display_header(width, height, screen, step):
    header = pygame.Surface((width, height))
    header.fill((255, 255, 255))
    msg = "Step: " + str(step)
    text_surface = font.render(msg, True, (0, 0, 0))
    screen.blit(header, (0, 0))
    screen.blit(text_surface, (20, 5))

def display_footer(width, offset, footer_height ,screen):
    footer = pygame.Surface((width, footer_height))
    footer.fill((255, 255, 255))  

    options = [
        "Choose algorithm:",
        "1. BFS          2. DFS          3. UCS",
        "4. A*           5. Greedy BFS   6. Dijkstra",
    ]


    # Render text
    screen.blit(footer, (0, offset))

    for i, line in enumerate(options):
        text_surface = font.render(line, True, (0, 0, 0))  # Black text
        screen.blit(text_surface, (20, offset + 5 + (i * 14))) 
