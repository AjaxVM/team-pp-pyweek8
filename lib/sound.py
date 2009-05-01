import os
import glob

import pygame

class SoundManager(object):
    sounds = {}
    music = {}
    def __init__(_, basepath):
        pygame.mixer.init()

        # load all sounds found in data
        for filename in glob.glob(os.path.join(basepath,'*.ogg')):
            stripped_filename = filename.replace(os.path.join(basepath,''), '')
            _.sounds[stripped_filename] = pygame.mixer.Sound(filename)

##        print "Loaded sounds:", `_.sounds.keys()`

    def __del__(_):
        pygame.mixer.quit()

