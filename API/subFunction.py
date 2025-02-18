import sys
import pygame
import string
import queue
import copy
import time

TIME_LIMITED = 1800

element_size = 32
wall = pygame.image.load('assets\images\wall.png')
floor = pygame.image.load('assets\images/floor.png')
box = pygame.image.load('assets\images/box.png')
box_docked = pygame.image.load('assets\images/box_docked.png')
worker = pygame.image.load('assets\images\worker.png')
worker_docked = pygame.image.load('assets\images\worker_dock.png')
docker = pygame.image.load('assets\images\dock.png')
background = 255, 226, 191

def validMove(state):
    x = 0
    y = 0
    move = []
    for step in ["U","D","L","R"]:
        if step == "U":
            x = 0
            y = -1
        elif step == "D":
            x = 0
            y = 1
        elif step == "L":
            x = -1
            y = 0
        elif step == "R":
            x = 1
            y = 0

        if state.can_move(x,y) or state.can_push(x,y):
            move.append(step)

    return move

def is_deadlock(state):
    box_list = state.box_list()
    for box in box_list:
        x = box[0]
        y = box[1]
        #corner up-left
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#' and state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#':
                    return True
                
        #corner up-right
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y+1) == '#':
                    return True


        #corner down-left
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#':
                    return True
                

        #corner down-right
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#' and state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#':
                    return True
                
    return False

def get_distance(state):
    sum = 0
    box_list = state.box_list()
    dock_list = state.dock_list()
    for box in box_list:
        for dock in dock_list:
            sum += (abs(dock[0] - box[0]) + abs(dock[1] - box[1]))
    return sum

def worker_to_box(state):
    p = 1000
    worker = state.worker()
    box_list = state.box_list()
    for box in box_list:
        if (abs(worker[0] - box[0]) + abs(worker[1] - box[1])) <= p:
            p = abs(worker[0] - box[0]) + abs(worker[1] - box[1])
    return p

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
                screen.blit(floor,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '@': #worker on floor
                screen.blit(worker,(x,y))
            elif char == '.': #dock
                screen.blit(docker,(x,y))
            elif char == '*': #box on dock
                screen.blit(box_docked,(x,y))
            elif char == '$': #box
                screen.blit(box,(x,y))
            elif char == '+': #worker on dock
                screen.blit(worker_docked,(x,y))
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


def BFS(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) # Parent Node                 
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"
    stateSet = queue.Queue()    # Queue to store traversed nodes 
    stateSet.put(state)
    stateExplored = []          # list of visited node (store matrix of nodes)
    print("Processing...")
    '''Traverse until there is no available node (No Solution)'''
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                    
        currState = stateSet.get()                      # get the top node of the queue to be the current node
        move = validMove(currState)                     # find next valid moves of current node in type of list of char ["U","D","L","R"]
        stateExplored.append(currState.get_matrix())    # add matrix of current node to visited list
        ''' For each valid move:
                Generate child nodes by updating the current node with move
                If the child node is not visited và not lead to deadlock (box on the corner), put it in queue of nodes
                If the child node is the end node to win, return the path of it'''
        for step in move:                               
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
        
            if newState.is_completed():
                end = time.time()
                print("Time to find solution:",round(end -start,2),"seconds")
                print("Number of visited node:",node_generated)
                print("Solution:",newState.pathSol)
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put(newState)
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"