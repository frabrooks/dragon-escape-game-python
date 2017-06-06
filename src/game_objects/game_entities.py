'''
Created on 6 Jun 2017

@author: Fraser
'''

import pygame
from pygame.locals import Rect
from abc import ABCMeta, abstractmethod



class SpriteO(pygame.sprite.Sprite):
    '''
    Sprite object for Entity etd_sprites
    '''


    def __init__(self, draw_layer):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.master_image = None
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
        self.draw_layer = draw_layer
        
    #Layer Property
    def _getLayer(self): return self.draw_layer
    def _setLayer(self, value): self.draw_layer = value
    Layer = property(_getLayer, _setLayer)
    
    
    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = Rect(0,0,width,height)
        self.columns = columns
        self.radius = width/5
        #try to auto calc total frames
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width// width) * (rect.height // height) - 1
        self.image = self.master_image.subsurface(rect)
        
    def update(self, current_time, rate=30):
        #update animation frame number
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame or self.frame < self.first_frame:
                self.frame = self.first_frame
            self.last_time = current_time

        #build current frame only if it changed
        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            self.image = self.master_image.subsurface(rect)
            self.old_frame = self.frame

    def __str__(self):
        return str(self.frame) + "," + str(self.first_frame) + \
               "," + str(self.last_frame) + "," + str(self.frame_width) + \
               "," + str(self.frame_height) + "," + str(self.columns) + \
               "," + str(self.rect)

class Entity(metaclass=ABCMeta):
    '''
    A drawable entity in the game
    '''
    
    def __init__(self, game):
        self.sprite_container = pygame.sprite.Group()
        self.game = game
       
    #X property
    def _getx(self): 
        i = -1
        for s in self.sprite_container.sprites():
            i = s.rect.x
        return i
    def _setx(self, value): 
        for s in self.sprite_container.sprites():
                s.rect.x = value
    X = property(_getx,_setx)


    #Y property
    def _gety(self):
        i = -1
        for s in self.sprite_container.sprites():
            i = s.rect.y
        return i
    def _sety(self,value): 
        for s in self.sprite_container.sprites():
                s.rect.y = value
    Y = property(_gety,_sety) 
    
    #position property
    def _getpos(self):
        i = -1,-1
        for s in self.sprite_container.sprites():
            i = s.rect.topleft
        return i
    def _setpos(self, pos):
        for s in self.sprite_container.sprites():
                s.rect.topleft = pos
    position = property(_getpos, _setpos)
    
    def draw(self, screen):
        self.sprite_container.draw(screen)
    
    def update(self, current_time, rate):
        for s in self.sprite_container.sprites():
            s.update(current_time, rate)
    
    def add_sprite(self, path, x, y, columns, layer, posX, posY):
        sprite = SpriteO(layer)
        sprite.load(path, x, y, columns)
        sprite.rect.topleft = (posX, posY)
        self.sprite_container.add(sprite)

        return sprite
    
    @abstractmethod
    def move(self):
        pass

    
    
            
            
            