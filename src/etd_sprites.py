'''
Created on 6 Jun 2017

@author: Fraser
'''
import pygame
from abc import ABCMeta, abstractmethod
from game_objects.game_entities import *
import math




class Obstacle(Entity, metaclass = ABCMeta):
    '''
    Abstract Animated Sprite representing an obstacle
    '''
    def __init__(self,  game):
        Entity.__init__(self, game)
        self.position = -1000, 195  # Initialise off west screen edge
    
    def move(self):
        game_speed = self.game.game_speed
        for s in self.sprite_container.sprites():
            s.rect.x -= game_speed
            
        if self.X < -520:
            return False
        else:              
            return True
    
    @abstractmethod
    def collide(self, player):
        pass
    
    @abstractmethod
    def game_over(self, game):
        pass
    
    def reset(self, x_rand):
        self.X = 2100 + x_rand
    
class Player(Entity):
    '''
    Animated Sprite representing the player
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/geoff_sprite_sheet.png", 256, 256, 8, 5, 675, 340) # Initialise at centre of viewport
        self.sprite.first_frame = 0
        self.sprite.last_frame = 7
        
        self.jump_height = 1.5
        self.jumping = False
        self.jumped = False
        self.sliding = False
        self.end_of_slide = False
        self.punching = False
        self.jump_vel = 0.0
        
        self.start_y = self.Y
        self.start_x = self.X
    
    def reset(self):
        self.sprite.first_frame = 0
        self.sprite.last_frame = 7
        self.sprite.frame = 0
        self.Y = self.start_y
        self.X = self.start_x
        self.jumping = False
        self.jumped = False
        self.sliding = False
        self.end_of_slide = False
        self.punching = False
        self.jump_vel = 0.0
    
    def move(self):
        if self.jumping:
            self.jump_vel = 0.6*math.pow((self.sprite.frame - 11.5), 3) * self.jump_height
            if self.jumped and self.sprite.frame == 8:
                self.reset()
            if self.sprite.frame == 15:
                self.jumped = True

        self.Y +=self.jump_vel

        if self.sliding:
            if self.end_of_slide and self.sprite.frame == 16:
                self.reset()
            if self.sprite.frame == 35:
                self.end_of_slide = True
                
        if self.punching and self.sprite.frame == 51:
            self.reset()
        
    def jump(self):
        if (self.sliding == False) and (self.punching == False) and (self.jumping == False):
            self.jumping = True
            self.sprite.first_frame = 8
            self.sprite.last_frame = 15
            self.sprite.frame = 8
            self.jump_time =  pygame.time.get_ticks()
            
    def punch(self):
        if (self.sliding == False) and (self.punching == False) and (self.jumping == False):
            self.punching = True
            self.sprite.first_frame = 44
            self.sprite.last_frame = 51
            self.sprite.frame = 44
        
    def slide(self):
        if (self.sliding == False) and (self.punching == False) and (self.jumping == False):
            self.sliding = True
            self.sprite.first_frame = 16
            self.sprite.last_frame = 35
            self.sprite.frame = 16
        
class Dragon(Entity):
    '''
    Animated Sprite representing the dragon
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/dragon_sprite_sheet.png", 600, 332, 4, 9, -808, 80) # Initialise to left of viewport
        self.done_moving = False
        
    def move(self):
        if (self.done_moving == False):
            if self.X < 4:
                self.X += 10
                if self.X > 4:
                    self.X = 4
                    self.done_moving = True

class TorchWall(Obstacle):
    '''
    Torch Wall Obstacle that the player slides under
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/torch_hurdle.png", 512, 512, 9, 6, -10000, 170) # Initialise to left of viewport
        self.back_sprite = self.add_sprite("../resources/torch_hurdle_back.png", 512, 512, 1, 4, -10000, 170) # Initialise at same point as foreground sprite
        
    def collide(self, player):
        for s in self.sprite_container.sprites():
            if pygame.sprite.collide_circle(s, player.sprite):
                if player.sliding:
                    return False
                return True
            return False
        print("Error: Collide() with no sprite. This should not happen!")
        return False
    
    def game_over(self, game):
        game.gameover_by_fire()
    
class Barricade(Obstacle):
    '''
    Barricade Obstacle that the player punches through
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/barricade_sprite_sheet.png", 512, 512, 4, 4, -10000, 118) # Initialise to left of viewport

        self.sprite.first_frame = 0
        self.sprite.last_frame = 0 # Barricade is static until broken
        self.is_broken = False
    
    def collide(self, player):
        for s in self.sprite_container.sprites():
            if pygame.sprite.collide_circle(s, player.sprite):
                if player.punching:
                    self.punched()
                    return False
                if self.is_broken:
                    return False
                return True
            return False
        print("Error: Collide() with no sprite. This should not happen!")
        return False
        
    def punched(self):
        self.is_broken = True
        self.sprite.last_frame = 7
        
    def reset(self, x_rand):
        self.is_broken = False
        self.sprite.first_frame = 0
        self.sprite.last_frame = 0
        self.sprite.frame = 0
        self.X = 2100 + x_rand
        
    def game_over(self, game):
        game.gameover_by_barricade()
    
class Pit(Obstacle):
    '''
    Pit Obstacle that the player jumps over
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/jump_gap.png", 512, 512, 1, 4, -10000, 195 ) # Initialise to left of viewport

    def collide(self, player):
        for s in self.sprite_container.sprites():
            if pygame.sprite.collide_circle(s, player.sprite):
                if player.jumping:
                    return False
                return True
            return False
        print("Error: Collide() with no sprite. This should not happen!")
        return False
    
    def game_over(self, game):
        game.gameover_by_gravity()
    
class Gui(Entity):
    '''
    The GUI
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.sprite = self.add_sprite("../resources/gui.png", 946, 205, 4, 10, 327, 150 ) # Initialise over centre
        self.sprite.first_frame = 0
        self.sprite.last_frame = 1
    
    def move(self):
        pass
        
class Background(Entity):
    '''
    The Background
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.bg_1 = self.add_sprite("../resources/backdrop.png", 1600, 800, 1, 0, 0,0 ) # Initialise over centre
        self.bg_2 = self.add_sprite("../resources/backdrop.png", 1600, 800, 1, 0, 1600,0 ) # Initialise over centre
        
    def move(self):
        game_speed = self.game.game_speed
        self.bg_1.rect.x -= game_speed
        self.bg_2.rect.x -= game_speed
        
        if self.bg_1.rect.x < -1600:
            self.bg_1.rect.x += 3200
        
        if self.bg_2.rect.x < -1600:
            self.bg_2.rect.x += 3200
            
class Foreground(Entity):
    '''
    The Background
    '''
    def __init__(self, game):
        Entity.__init__(self, game)
        
        self.bg_1 = self.add_sprite("../resources/front_wall.png", 1600, 800, 1, 8, 0,0 ) # Initialise over centre
        self.bg_2 = self.add_sprite("../resources/front_wall.png", 1600, 800, 1, 8, 1600,0 ) # Initialise over centre
    
    def move(self):
        game_speed = self.game.game_speed
        self.bg_1.rect.x -= game_speed
        self.bg_2.rect.x -= game_speed
        
        if self.bg_1.rect.x < -1600:
            self.bg_1.rect.x += 3200
        
        if self.bg_2.rect.x < -1600:
            self.bg_2.rect.x += 3200
        
        
        
        
        