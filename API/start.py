import sys
import pygame
import string
import queue
import copy
import time

def LoadMap(file_name):
    with open(file_name, 'r') as file:
        grid = file.readlines()
        return grid

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

def DisplayBox(screen, message):
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

def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  DisplayBox(screen, question + ": " + "".join(current_string))
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
    DisplayBox(screen, question + ": " + "".join(current_string))
  return "".join(current_string)

def StartGame():
    start = pygame.display.set_mode((320,240))
    level = ask(start,"Select Level")
    if int (level) > 0:
        return level
    else:
        print("ERROR: Invalid Level: "+str(level))
        sys.exit(2)