import sys
import pygame
import os
import copy
import time
from API.game import *
from API.start import *
from Algorithms.sokoban import *

def main():
    pygame.init()
    level = StartGame()
    game = Game(map_open(level))
    size = game.load_size()
    width = game.get_width()
    height = game.get_height()
    header_height = 64
    footer_height = 70
    screen = pygame.display.set_mode((width, height + header_height + footer_height))
    sol = ""
    output = {}
    i = 0
    flagAuto = 0
    flagReset = 1
    flagEnd = 0
    reset_matrix = copy.deepcopy(game.get_matrix())
    if int(level) < 10:
        file = "input-0"+level+".txt"
    else:
        file = "input-"+level+".txt"
    file_path = os.path.join("assets", "input", file)

    while True :
        print_game(game.get_matrix(),screen)
        display_footer(width, height + header_height, footer_height, screen)
        if flagEnd:
            display_header_final(width, header_height, screen, output)
        else:
            display_header(width, header_height, screen, game.get_step())

        if sol == "No Solution":
            display_information(screen,"Cannot")
            flagAuto = 0
        if sol == "TimeOut":
            display_information(screen,"Out")
            flagAuto = 0
        if game.is_completed():
            display_information(screen,"Done")

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: 
                    sys.exit(0)
                elif event.key == pygame.K_r:
                    game.reset(reset_matrix)
                    pygame.display.flip()
                    sol = ""
                elif sol != "No Solution" and sol != "TimeOut" and sol != "complete":
                    if event.key == pygame.K_1:
                        display_information(screen,"BFS")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("BFS is running")
                        output = bfs(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_2:
                        display_information(screen,"DFS")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("DFS is running")
                        output = dfs(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_3:
                        display_information(screen,"UCS")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("UCS is running")
                        output = ucs(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_4:
                        display_information(screen,"A*")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("A* is running")
                        output = astar(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_5:
                        display_information(screen,"GBFS")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("GBFS is running")
                        output = gbfs(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_6:
                        display_information(screen,"Swarm")
                        pygame.display.flip()
                        game.reset(reset_matrix)
                        print("Swarm is running")
                        output = swarm(file_path)
                        flagAuto = True
                        if output == "No Solution":
                            sol = "No Solution"
                        elif output == "TimeOut":
                            sol = "TimeOut"
                        else:
                            sol = output["Path"]
                        print(output)
                    elif event.key == pygame.K_UP:
                        game.Ares_move("U")
                    elif event.key == pygame.K_DOWN:
                        game.Ares_move("D")
                    elif event.key == pygame.K_LEFT:
                        game.Ares_move("L")
                    elif event.key == pygame.K_RIGHT:
                        game.Ares_move("R")
                    elif event.key == pygame.K_p:
                        flagAuto = 1 - flagAuto #pause

        if (flagAuto) and (i < len(sol)):
            if (i==0):
                flagEnd = 0
                game.reset(reset_matrix)
                time.sleep(0.5)
            playByBot(game,sol[i].upper())
            i += 1
            if i == len(sol): 
                flagEnd = 1
                flagAuto = 0
                i = 0
                time.sleep(0.1)
                sol = "complete"
            time.sleep(0.1)

        pygame.display.update()

if __name__ == '__main__':
    main()
