import sys
import pygame
import os
import copy
import time
from API.game import *
from API.start import *
from API.subFunction import *
from Algorithms.sokoban import *

def main():
    pygame.init()
    level = StartGame()
    game = Game(map_open(level))
    size = game.load_size()
    width = game.get_width()
    height = game.get_height()
    header_height = 64
    footer_height = 64
    screen = pygame.display.set_mode((width, height + header_height + footer_height))
    sol = ""
    i = 0
    flagAuto = 0
    reset_matrix = copy.deepcopy(game.get_matrix())
    if int(level) < 10:
        file = "input-0"+level+".txt"
    else:
        file = "input-"+level+".txt"
    file_path = os.path.join("assets", "input", file)

    while True:
        print_game(game.get_matrix(),screen)
        display_header(width, header_height, screen, game.get_step())
        display_footer(width, height + header_height, footer_height, screen)

        if sol == "NoSol":
            display_end(screen,"Cannot")
        if sol == "TimeOut":
            display_end(screen,"Out")
        if game.is_completed():
            display_end(screen,"Done")

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    output = bfs(file_path)
                    flagAuto = True
                    if output == "No Solution":
                        sol = "NoSol"
                    else:
                        sol = output["Path"]
                    print(sol)
                elif event.key == pygame.K_2:
                    output = dfs(file_path)
                    flagAuto = True
                    if output == "No Solution":
                        sol = "NoSol"
                    else:
                        sol = output["Path"]
                    print(sol)
                elif event.key == pygame.K_3:
                    output = ucs(file_path)
                    flagAuto = True
                    if output == "No Solution":
                        sol = "NoSol"
                    else:
                        sol = output["Path"]
                    print(sol)
                elif event.key == pygame.K_4:
                    output = astar(file_path)
                    flagAuto = True
                    if output == "No Solution":
                        sol = "NoSol"
                    else:
                        sol = output["Path"]
                    print(sol)
                elif event.key == pygame.K_5:
                    output = gbfs(file_path)
                    flagAuto = True
                    if output == "No Solution":
                        sol = "NoSol"
                    else:
                        sol = output["Path"]
                    print(sol)
                elif event.key == pygame.K_UP: 
                    game.move(0,-1, True)
                elif event.key == pygame.K_DOWN: 
                    game.move(0,1, True)
                elif event.key == pygame.K_LEFT: 
                    game.move(-1,0, True)
                elif event.key == pygame.K_RIGHT: 
                    game.move(1,0, True)
                elif event.key == pygame.K_q: 
                    sys.exit(0)
                elif event.key == pygame.K_d: 
                    game.unmove()
                elif event.key == pygame.K_c: 
                    sol = ""
                elif event.key == pygame.K_p:
                    flagAuto = 1 - flagAuto #pause
                elif event.key == pygame.K_r:
                    game.reset(reset_matrix)

        if (flagAuto) and (i < len(sol)):
            playByBot(game,sol[i].upper())
            i += 1
            if i == len(sol): 
                flagAuto = 0
            time.sleep(0.2)

        pygame.display.update()
    
if __name__ == '__main__':
    main()
