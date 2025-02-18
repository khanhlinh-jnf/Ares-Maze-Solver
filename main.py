import sys
import pygame
import string
import queue
import copy
import time
from API.game import *
from API.start import *
from API.subFunction import *

def main():
    pygame.init()
    level = StartGame()
    game = Game(map_open(level))
    size = game.load_size()
    screen = pygame.display.set_mode(size)
    sol = ""
    i = 0
    flagAuto = 0
    width = game.get_width()
    height = 32

    while True:
      print_game(game.get_matrix(),screen)
      display_header(width, height, screen, game.get_step())

      if sol == "NoSol":
          display_end(screen,"Cannot")
      if sol == "TimeOut":
          display_end(screen,"Out")
      if game.is_completed():
          display_end(screen,"Done")

      for event in pygame.event.get():
          if event.type == pygame.QUIT: sys.exit(0)
          elif event.type == pygame.KEYDOWN:
              # if event.key == pygame.K_a:
              #     sol = AstarSolution(game)
              #     flagAuto = 1
              # elif event.key == pygame.K_b:
              #     sol = BFSsolution(game)
              #     flagAuto = 1
              if event.key == pygame.K_UP: 
                  game.move(0,-1, True)
              elif event.key == pygame.K_DOWN: 
                  game.move(0,1, True)
              elif event.key == pygame.K_LEFT: 
                  game.move(-1,0, True)
              elif event.key == pygame.K_RIGHT: 
                  game.move(1,0, True)
              elif event.key == pygame.K_q: sys.exit(0)
              elif event.key == pygame.K_d: 
                  game.unmove()
              elif event.key == pygame.K_c: sol = ""

      if (flagAuto) and (i < len(sol)):
          playByBot(game,sol[i])
          i += 1
          if i == len(sol): flagAuto = 0
          time.sleep(0.1)

      pygame.display.update()
    
if __name__ == '__main__':
    main()
