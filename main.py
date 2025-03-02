import sys
import pygame
import os
import copy
import time
from API.class_game import *
from API.func_ui import *
from API.algorithms import *
import threading

writting = False
solving = False
sol = ""
output = {}
i = 0
flagAuto = 0
flagSolve = 0
name_algo = ""


def save_output(level):
    global writting
    writting = True
    write_result_to_output(level)
    writting = False


def run_algorithm(algo_name, algo_func, file_path, game, reset_matrix, screen):
    global output, sol, flagAuto, flagSolve, name_algo, solving
    name_algo = algo_name
    solving = True
    display_information(screen, algo_name)
    game.reset(reset_matrix)
    output = algo_func(file_path)
    pygame.display.flip()
    flagAuto = True
    flagSolve = 1
    if output == "No Solution":
        sol = "No Solution"
    elif output == "TimeOut":
        sol = "TimeOut"
    else:
        sol = output["Path"]
    solving = False


def main():
    global sol, i, flagAuto, flagSolve, output, name_algo, solving
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("assets\\background_music.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    pygame.display.set_caption("Ares's Adventure")
    firstLogin = True
    music = True

    # Check valid level
    while True:
        level, flag = StartGame(firstLogin)
        firstLogin = False
        if flag:
            break

    game = Game()
    game.map_open(level)
    game.GetStonesDict()
    caption = "Ares's Adventure - Level " + level
    pygame.display.set_caption(caption)
    width = game.get_width()
    height = game.get_height()
    header_height = 64
    footer_height = 70
    flagReset = 1
    flagEnd = 0

    screen = pygame.display.set_mode((width, height + header_height + footer_height))

    reset_matrix = copy.deepcopy(game.get_matrix())
    if int(level) < 10:
        file = "input-0" + level + ".txt"
    else:
        file = "input-" + level + ".txt"
    file_path = os.path.join("input", file)

    while True:
        print_game(game.get_matrix(), screen, header_height)

        display_footer(width, height + header_height, footer_height, screen)
        if flagEnd:
            display_header_final(width, header_height, screen, output)
        else:
            display_header(
                width, header_height, screen, game.get_step(), game.get_weight()
            )

        if sol == "No Solution":
            display_information(screen, "Cannot")
            flagAuto = 0
        if sol == "TimeOut":
            display_information(screen, "Out")
            flagAuto = 0
        if game.is_completed():
            display_information(screen, "Done")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and writting == False:
                if event.key == pygame.K_q:
                    sys.exit(0)
                elif event.key == pygame.K_r:
                    game.reset(reset_matrix)
                    pygame.display.flip()
                    sol = ""
                    flagSolve = 0
                    flagAuto = 0
                    flagEnd = 0
                    i = 0
                elif event.key == pygame.K_o:
                    if sol == "Complete" or sol == "No Solution" or sol == "TimeOut" or sol != "":
                        continue
                    if not writting:
                        threading.Thread(
                            target=save_output, args=(level,), daemon=True
                        ).start()
                elif event.key == pygame.K_p:
                    if sol == "Complete":
                        continue
                    flagAuto = 1 - flagAuto  # pause
                elif event.key == pygame.K_m:
                    if music:
                        pygame.mixer.music.pause()
                        music = False
                    else:
                        pygame.mixer.music.unpause()
                        music = True
                elif (
                    solving == False
                    and sol != "No Solution"
                    and sol != "TimeOut"
                    and sol != "Complete" and sol == ""
                ):
                    if event.key == pygame.K_1:
                        threading.Thread(
                            target=run_algorithm,
                            args=("BFS", bfs, file_path, game, reset_matrix, screen),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_2:
                        threading.Thread(
                            target=run_algorithm,
                            args=("DFS", dfs, file_path, game, reset_matrix, screen),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_3:
                        threading.Thread(
                            target=run_algorithm,
                            args=("UCS", ucs, file_path, game, reset_matrix, screen),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_4:
                        threading.Thread(
                            target=run_algorithm,
                            args=("A*", astar, file_path, game, reset_matrix, screen),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_5:
                        threading.Thread(
                            target=run_algorithm,
                            args=("GBFS", gbfs, file_path, game, reset_matrix, screen),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_6:
                        threading.Thread(
                            target=run_algorithm,
                            args=(
                                "WA",
                                weighted_astar,
                                file_path,
                                game,
                                reset_matrix,
                                screen,
                            ),
                            daemon=True,
                        ).start()
                    elif event.key == pygame.K_UP:
                        game.Ares_move("U")
                    elif event.key == pygame.K_DOWN:
                        game.Ares_move("D")
                    elif event.key == pygame.K_LEFT:
                        game.Ares_move("L")
                    elif event.key == pygame.K_RIGHT:
                        game.Ares_move("R")

        if (flagAuto) and (i < len(sol)):
            if i == 0:
                flagEnd = 0
                game.reset(reset_matrix)
                time.sleep(0.5)
            playByBot(game, sol[i].upper())
            i += 1
            if i == len(sol):
                flagEnd = 1
                flagAuto = 0
                i = 0
                time.sleep(0.1)
                sol = "Complete"
            time.sleep(0.1)

        if solving:
            display_information(screen, name_algo)
            continue
        if writting:
            display_information(screen, "Output")
            continue
        pygame.display.update()


if __name__ == "__main__":
    main()
