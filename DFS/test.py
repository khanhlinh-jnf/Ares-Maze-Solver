import sys
import os
import string
import queue
import copy
import time

class Game:
    def __init__(self, matrix):
        self.stack = []
        self.matrix = matrix
        self.path = ""
        self.weightList = []
        self.weight = 0
        self.stoneDict = {}

    def IsValidValue(self, value):
        if (value == '#' #wall
        or value == ' ' #space
        or value == '$' #stone
        or value == '@' #ares
        or value == '.' #switch
        or value == '*' #stone on switch
        or value == '+'): #ares on switch
            return True
        else:
            return False

    def GetMap(self, filename, level):
        if not os.path.exists(filename):
            print(f"ERROR: File '{filename}' not found")
            sys.exit(1)
        if (level < 1 or level > 10):
            print("ERROR: Level "+str(level)+" is out of range")
            sys.exit(1)
        else:
            levelFound = False
            numFound = False
            with open(filename) as file:
                for line in file:
                    if not levelFound:
                        if line.strip() == "Level "+str(level):
                            levelFound = True
                    elif levelFound and not numFound:
                        numLine = line.strip()
                        self.weightList.extend(map(int, numLine.split()))
                        numFound = True
                    else:
                        if line.strip() == "":
                            break
                        else:
                            row = []
                            for char in line.strip('\n'):
                                if (char != '\n' and char in ['#', ' ', '$', '@', '.', '*', '+']):
                                    row.append(char)
                                else:
                                    print("ERROR: Level "+str(level)+" has '"+char+"' is not a valid character")
                                    sys.exit(1)
                            self.matrix.append(row)
            if not levelFound:
                print("ERROR: Level "+str(level)+" not found")
                sys.exit(1)
            
            self.GetStonesDict()
        

    def GetContent(self, x, y):
        return self.matrix[y][x]

    def SetContent(self, x, y, content):
        if self.IsValidValue(content):
            self.matrix[y][x] = content
        else:
            print("Error: '" + content + "' is not a valid value")
    
    def Ares(self):
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                x += 1
            x = 0
            y += 1
        raise ValueError("Ares not found in the matrix")
        
    def GetStones(self):
        stones = []
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '$' or pos == '*':
                    stones.append((x, y))
                x += 1
            x = 0
            y += 1
        return stones

    def GetStonesDict(self):
        stones = self.GetStones()
        for stone, value in zip(stones, self.weightList):
            self.stoneDict[stone] = value
        return self.stoneDict

    def GetSwitches(self):
        switches = []
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '.' or pos == '+' or pos == '*':
                    switches.append((x, y))
                x += 1
            x = 0
            y += 1
        return switches

    def GetMatrix(self):
        return self.matrix

    def Next(self, x, y):
        return (self.Ares()[0]+x, self.Ares()[1]+y)

    def CanMove(self, x, y):
        next_x, next_y = self.Next(x, y)
        return self.GetContent(next_x, next_y) in [' ', '.']

    def CanPush(self, x, y):
        next_x, next_y = self.Next(x, y)
        next_next_x, next_next_y = self.Next(x + x, y + y)
        return (self.GetContent(next_x, next_y) in ['*','$'] and self.GetContent(next_next_x, next_next_y) in [' ','.'])

    def IsCompleted(self):
        for row in self.matrix:
            for pos in row:
                if pos == '$':
                    return False
        return True

    def MoveStone(self, x, y, a, b):
        #move step: x y 
        #stone coordinates: a b
        if self.GetContent(a,b) == '$':
            self.SetContent(a,b,' ')
            if self.GetContent(a+x,b+y) == '.':
                self.SetContent(a+x,b+y,'*')
            else:
                self.SetContent(a+x,b+y,'$')
            
        if self.GetContent(a,b) == '*':
            self.SetContent(a,b,'.')
            if self.GetContent(a+x,b+y) == '.':
                self.SetContent(a+x,b+y,'*')
            else:
                self.SetContent(a+x,b+y,'$')

    def Move(self, x, y):
        ares_x, ares_y, ares_char = self.Ares()
        next_x, next_y = self.Next(x, y)

        if self.CanMove(x, y):
            self.weight += 1
            if ares_char == '@':
                self.SetContent(ares_x, ares_y, ' ')
                if self.GetContent(next_x, next_y) == '.':
                    self.SetContent(next_x, next_y, '+')
                else:
                    self.SetContent(next_x, next_y, '@')
                
            if ares_char == '+':
                self.SetContent(ares_x, ares_y, '.')
                if self.GetContent(next_x, next_y) == '.':
                    self.SetContent(next_x, next_y, '+')
                else:
                    self.SetContent(next_x, next_y, '@')

        elif self.CanPush(x, y):
            self.weight += self.stoneDict.get((next_x, next_y))
            self.stoneDict[(next_x+x, next_y+y)] = self.stoneDict.pop((next_x, next_y))
            self.MoveStone(x, y, next_x, next_y)
            if ares_char == '@':
                self.SetContent(ares_x, ares_y, ' ')
                if self.GetContent(next_x, next_y) == '.':
                    self.SetContent(next_x, next_y, '+')
                else:
                    self.SetContent(next_x, next_y, '@')
            if ares_char == '+':
                self.SetContent(ares_x, ares_y, '.')
                if self.GetContent(next_x, next_y) == '.':
                    self.SetContent(next_x, next_y, '+')
                else:
                    self.SetContent(next_x, next_y, '@')

direction = [(0, -1), (0, 1), (-1, 0), (1, 0)] #up, down, left, right

def ValidMove(state):
    moves = []
    ares_x, ares_y, ares_char = state.Ares()
    index = 0
    for move in ['u', 'd', 'l', 'r']:
        x, y = direction[index]
        next_x, next_y = state.Next(x, y)
        if state.CanMove(x, y):
            moves.append(move)
        elif state.CanPush(x, y):
            moves.append(move.upper())
        index += 1
    return moves


'''def IsDeadlock(state):
    stoneList = state.GetStones()
    
    for stone in stoneList:
        blockSide = 0  
        
        for dir in direction:
            next_x, next_y = stone[0] + dir[0], stone[1] + dir[1]
            next_content = state.GetContent(next_x, next_y)

            if next_content == '#':
                blockSide += 1

            elif next_content in ['$', '*']:  
                next_next_x, next_next_y = stone[0] + dir[0] * 2, stone[1] + dir[1] * 2
                next_next_content = state.GetContent(next_next_x, next_next_y)

                if next_next_content == '#':
                    blockSide += 1
        
        if blockSide >= 2:
            return True 
    
    return False  '''


def IsDeadlock(state):
    stone_list = state.GetStones()
    for stone in stone_list:
        x = stone[0]
        y = stone[1]
        #corner up-left
        if state.GetContent(x,y-1) in ['#','$','*'] and state.GetContent(x-1,y) in ['#','$','*']:
            if state.GetContent(x-1,y-1) in ['#','$','*']:
                return True
            if state.GetContent(x,y-1) == '#' and state.GetContent(x-1,y) =='#':
                return True
            if state.GetContent(x,y-1) in ['$','*'] and state.GetContent(x-1,y) in ['$','*']:
                if state.GetContent(x+1,y-1) == '#' and state.GetContent(x-1,y+1) == '#':
                    return True
            if state.GetContent(x,y-1) in ['$','*'] and state.GetContent(x-1,y) == '#':
                if state.GetContent(x+1,y-1) == '#':
                    return True
            if state.GetContent(x,y-1) == '#' and state.GetContent(x-1,y) in ['$','*']:
                if state.GetContent(x-1,y+1) == '#':
                    return True
                
        #corner up-right
        if state.GetContent(x,y-1) in ['#','$','*'] and state.GetContent(x+1,y) in ['#','$','*']:
            if state.GetContent(x+1,y-1) in ['#','$','*']:
                return True
            if state.GetContent(x,y-1) == '#' and state.GetContent(x+1,y) =='#':
                return True
            if state.GetContent(x,y-1) in ['$','*'] and state.GetContent(x+1,y) in ['$','*']:
                if state.GetContent(x-1,y-1) == '#' and state.GetContent(x+1,y+1) == '#':
                    return True
            if state.GetContent(x,y-1) in ['$','*'] and state.GetContent(x+1,y) == '#':
                if state.GetContent(x-1,y-1) == '#':
                    return True
            if state.GetContent(x,y-1) == '#' and state.GetContent(x+1,y) in ['$','*']:
                if state.GetContent(x+1,y+1) == '#':
                    return True


        #corner down-left
        elif state.GetContent(x,y+1) in ['#','$','*'] and state.GetContent(x-1,y) in ['#','$','*']:
            if state.GetContent(x-1,y+1) in ['#','$','*']:
                return True
            if state.GetContent(x,y+1) == '#' and state.GetContent(x-1,y) =='#':
                return True
            if state.GetContent(x,y+1) in ['$','*'] and state.GetContent(x-1,y) in ['$','*']:
                if state.GetContent(x-1,y-1) == '#' and state.GetContent(x+1,y+1) == '#':
                    return True
            if state.GetContent(x,y+1) in ['$','*'] and state.GetContent(x-1,y) == '#':
                if state.GetContent(x+1,y+1) == '#':
                    return True
            if state.GetContent(x,y+1) == '#' and state.GetContent(x-1,y) in ['$','*']:
                if state.GetContent(x-1,y-1) == '#':
                    return True
                

        #corner down-right
        elif state.GetContent(x,y+1) in ['#','$','*'] and state.GetContent(x+1,y) in ['#','$','*']:
            if state.GetContent(x+1,y+1) in ['#','$','*']:
                return True
            if state.GetContent(x,y+1) == '#' and state.GetContent(x+1,y) =='#':
                return True
            if state.GetContent(x,y+1) in ['$','*'] and state.GetContent(x+1,y) in ['$','*']:
                if state.GetContent(x-1,y+1) == '#' and state.GetContent(x+1,y-1) == '#':
                    return True
            if state.GetContent(x,y+1) in ['$','*'] and state.GetContent(x+1,y) == '#':
                if state.GetContent(x-1,y+1) == '#':
                    return True
            if state.GetContent(x,y+1) == '#' and state.GetContent(x+1,y) in ['$','*']:
                if state.GetContent(x+1,y-1) == '#':
                    return True
                
    return False



def PrintMatrix(matrix):
    for row in matrix:
        for char in row:
            sys.stdout.write(char)
            sys.stdout.flush()
        sys.stdout.write('\n')



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


def DFS(game):
    start = time.time()
    node_count = 0
    state = copy.deepcopy(game)
    node_count += 1
    if IsDeadlock(state):
        end = time.time()
        print("Deadlock detected")
        print("Time to find solution:", round(end - start, 2), "seconds")
        print("Number of visited node: ", node_count)
        print("No solution")
        return False
    stateSet = Stack()
    stateSet.push(state)
    stateExplored = []
    while not stateSet.empty():
        currentState = stateSet.pop()
        moves = ValidMove(currentState)
        stateExplored.append(currentState.GetMatrix())
        for move in moves:
            step = move.lower()
            newState = copy.deepcopy(currentState)
            node_count += 1
            if step == 'u':    
                newState.Move(0, -1)
            elif step == 'd':
                newState.Move(0, 1)
            elif step == 'l':
                newState.Move(-1, 0)
            elif step == 'r':
                newState.Move(1, 0)
            newState.path += move

            if newState.IsCompleted():
                end = time.time()
                print("Solution found")
                print("Time to find solution:", round(end - start, 2), "seconds")
                print("Number of visited node: ", node_count)
                print("Total weight: ", newState.weight)
                print("Solution path: ", newState.path)
                return True

            if (newState.GetMatrix() not in stateExplored) and (not IsDeadlock(newState)):
                stateSet.push(newState)
    
    end = time.time()
    print("Failed to find solution")
    print("Time to find solution:", round(end - start, 2), "seconds")
    print("Number of visited node: ", node_count)
    print("No solution")
    return False


def main():
    state = Game([])
    state.GetMap("levels", 1)
    PrintMatrix(state.GetMatrix())
    DFS(state)


if __name__ == "__main__":
    main()