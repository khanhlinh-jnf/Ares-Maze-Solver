import sys
import pygame
import string
import queue
import copy
import time

TIME_LIMITED = 1800

class Game:

    def is_valid_value(self,char):
        if ( char == ' ' or #floor
            char == '#' or #wall
            char == '@' or #worker on floor
            char == '.' or #dock
            char == '*' or #box on dock
            char == '$' or #box
            char == '+' ): #worker on dock
            return True
        else:
            return False

    def __init__(self,matrix):
        self.heuristic = 0
        self.pathSol = ""
        self.stack = []
        self.matrix = matrix

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

    def print_matrix(self):
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):
        return self.matrix[y][x]

    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def box_list(self):
        x = 0
        y = 0
        boxList = []
        for row in self.matrix:
            for pos in row:
                if pos == '$':
                    boxList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return boxList

    def dock_list(self):
        x = 0
        y = 0
        dockList = []
        for row in self.matrix:
            for pos in row:
                if pos == '.':
                    dockList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return dockList

    def can_move(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#','*','$']

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y):
        return (self.next(x,y) in ['*','$'] and self.next(x+x,y+y) in [' ','.'])

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b):
#        (x,y) -> move to do
#        (a,b) -> box to move
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')

    def unmove(self):
        if len(self.stack) > 0:
            movement = self.stack.pop()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
        elif self.can_push(x,y):
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)
            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))

''' Find next valid moves of a node: worker can move into a space or can push a box'''
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

''' Check deadlock: box on the corner of walls or other boxes   '''
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

''' Algorithms return path to win the game in type of string:
        U: move up
        D: move down
        L: move left
        R: move right
    If there is no solution, return string "NoSol" '''


class Stack:
    def __init__(self):
        self.stack = []
    def push(self, item):
        self.stack.append(item)
    def pop(self):
        return self.stack.pop()
    def empty(self):
        return len(self.stack) == 0
    def size(self):
        return len(self.stack)
    def get(self):
        return self.stack[-1]

def DFSsolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) # Parent Node                 
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end - start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"
    stateSet = Stack()   # Stack to store traversed nodes 
    stateSet.push(state)
    stateExplored = []          # list of visited node (store matrix of nodes)
    print("Processing...")
    '''Traverse until there is no available node (No Solution)'''
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                    
        currState = stateSet.get()                      # get the top node of the queue to be the current node
        currState = stateSet.pop()
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
                stateSet.push(newState)
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"

def AstarSolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) # Parent Node
    state.heuristc = worker_to_box(state) + get_distance(state)
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"                 
    stateSet = queue.PriorityQueue()    # Queue to store traversed nodes (low index -> high priority) 
    stateSet.put(state)
    stateExplored = []                 # list of visited node (store matrix of nodes)
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
            newState.heuristic = worker_to_box(newState) + get_distance(newState)
        
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

def map_open(filename, level):
    matrix = []
#   if level < 1 or level > 50:
    if int(level) < 1:
        print("ERROR: Level "+str(level)+" is out of range")
        sys.exit(1)
    else:
        file = open(filename,'r')
        level_found = False
        for line in file:
            row = []
            if not level_found:
                if  "Level "+str(level) == line.strip():
                    level_found = True
            else:
                if line.strip()!= "":
                    row = []
                    for c in line:
                        if c != '\n' and c in [' ','#','@','+','$','*','.']:
                            row.append(c)
                        elif c == '\n': #jump to next row when newline
                            continue
                        else:
                            print("ERROR: Level "+str(level)+" has invalid value "+c)
                            sys.exit(1)
                    matrix.append(row)
                else:
                    break
        return matrix

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
  fontobject = pygame.font.Font(None,18)
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
  pygame.display.flip()

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
    start = pygame.display.set_mode((320,240))
    level = ask(start,"Select Level")
    if int (level) > 0:
        return level
    else:
        print("ERROR: Invalid Level: "+str(level))
        sys.exit(2)

wall = pygame.image.load('.\images\wall.png')
floor = pygame.image.load('.\images/floor.png')
box = pygame.image.load('.\images/box.png')
box_docked = pygame.image.load('.\images/box_docked.png')
worker = pygame.image.load('.\images\worker.png')
worker_docked = pygame.image.load('.\images\worker_dock.png')
docker = pygame.image.load('.\images\dock.png')
background = 255, 226, 191
pygame.init()

level = start_game()
game = Game(map_open('.\levels',level))
size = game.load_size()
screen = pygame.display.set_mode(size)
sol = ""
#sol = BFSsolution(game)
#sol = AstarSolution(game)
i = 0
flagAuto = 0
while 1:
    print_game(game.get_matrix(),screen)

    if sol == "NoSol":
        display_end(screen,"Cannot")
    if sol == "TimeOut":
        display_end(screen,"Out")
    if game.is_completed():
        display_end(screen,"Done")

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                sol = AstarSolution(game)
                flagAuto = 1
            elif event.key == pygame.K_b:
                sol = DFSsolution(game)
                flagAuto = 1
            elif event.key == pygame.K_UP: game.move(0,-1, True)
            elif event.key == pygame.K_DOWN: game.move(0,1, True)
            elif event.key == pygame.K_LEFT: game.move(-1,0, True)
            elif event.key == pygame.K_RIGHT: game.move(1,0, True)
            elif event.key == pygame.K_q: sys.exit(0)
            elif event.key == pygame.K_d: game.unmove()
            elif event.key == pygame.K_c: sol = ""

    if (flagAuto) and (i < len(sol)):
        playByBot(game,sol[i])
        i += 1
        if i == len(sol): flagAuto = 0
        time.sleep(0.1)

    pygame.display.update()
