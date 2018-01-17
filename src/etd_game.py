'''
# Escape the Dragon Game
Created on 5 Jun 2016

@author: Fraser
'''

import sys, math, pygame
from pygame.locals import QUIT, K_ESCAPE, K_SPACE, K_d, K_s
import etd_sprites
from random import randint


def print_text(font, x, y, text, screen, color=(255,255,255)):
    imgText = font.render(text, True, color)
    screen.blit(imgText, (x,y))


class MainGame (object):
    
    
    def __init__(self, screen):
        self.screen = screen
        self.rand_start()

        self.entities = []
        self.bg = etd_sprites.Background(self)
        self.entities.append(self.bg)
        self.fg = etd_sprites.Foreground(self)
        self.entities.append(self.fg)
        self.dragon = etd_sprites.Dragon(self)
        self.entities.append(self.dragon)
        self.player = etd_sprites.Player(self)
        self.entities.append(self.player)
        
        self.gui = etd_sprites.Gui(self)
        
        self.obstacles = []
        self.torch = etd_sprites.TorchWall(self)
        self.obstacles.append(self.torch)
        self.pit = etd_sprites.Pit(self)
        self.obstacles.append(self.pit)
        self.barricade = etd_sprites.Barricade(self)
        self.obstacles.append(self.barricade)
        
        self.current_obstacle = self.pit

        # Sprite group with support for sprite layers
        self.scene = pygame.sprite.LayeredUpdates()
        for entity in self.entities + self.obstacles:
            for sprite in entity.sprite_container.sprites():
                self.scene.add(sprite, layer = sprite.draw_layer )
        
        self.player_sprite = self.scene.get_sprites_from_layer(5)[0]    
        
        self.game_over = False
        self.game_started = False
        self.game_speed = 32
        self.last_speed_change = 0
        self.score = 0
        
        self.main_loop()
        
    def main_loop(self):
        while True:
            self.wait_for_input()
            self.play()
            
            #Reset everything to play again
            self.score = 0
            for o in self.obstacles:
                o.reset(-4000)
            self.player.reset()
            self.dragon.X = -808
            self.dragon.done_moving = False
            self.game_speed = 32
            self.last_speed_change = 0
            self.game_over = False
            self.game_started = False
            self.gui.sprite.first_frame = 0
            self.gui.sprite.last_frame = 1
            self.scene.change_layer(self.player_sprite, 5)
            
    def wait_for_input(self):
        while (not self.game_started):
            framerate.tick(30)
            ticks = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif keys[K_SPACE]:
                self.player.reset()
                self.game_started = True
                
            self.bg.move()
            self.fg.move()
            
            self.bg.update(ticks, 50)
            self.player.update(ticks, 50)
            self.fg.update(ticks, 50)
            self.gui.update(ticks, 400)
            

            self.bg.draw(self.screen)
            self.player.draw(self.screen)
            self.fg.draw(self.screen)

            self.gui.draw(self.screen)
            
            pygame.display.update()
    
    def play(self):
        while (not self.game_over):
            framerate.tick(30)
            ticks = pygame.time.get_ticks()
            self.score += 0.05
            
            if abs(ticks - self.last_speed_change) > 2000:
                self.last_speed_change = ticks
                self.game_speed += 1
                if self.game_speed > 40:
                    self.game_speed = 40
            
            for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()
                        sys.exit()
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif keys[K_SPACE]:
                self.player.jump()
            elif keys[K_s]:
                self.player.slide()
            elif keys[K_d]:
                self.player.punch()
            
            for s in self.entities:
                s.move()

            if (not self.current_obstacle.move()):
                self.current_obstacle = self.obstacles[self.next_rand()]
                self.current_obstacle.reset(randint(0,600))
            
            if ( self.current_obstacle.collide(self.player)):
                self.current_obstacle.game_over(self)
                self.game_over = True
            
            if (self.barricade.is_broken == True) and (self.barricade.sprite.frame == 7):
                self.barricade.sprite.first_frame = 7
            
            if (self.game_over == False):
                self.bg.update(ticks, 50)
                self.fg.update(ticks, 50)
                if self.player.jumping:
                    self.player.update(ticks, 100*(25/self.game_speed))
                elif self.player.sliding:
                    self.player.update(ticks, 45*(25/self.game_speed))
                else:
                    self.player.update(ticks, 50)
                self.current_obstacle.update(ticks, 50)
                self.dragon.update(ticks, 150)
            
            
            self.render_scene()
            print_text(font1, 1400, 20, "Score: ", self.screen)
            print_text(font1, 1500, 20, str(int(self.score*self.game_speed)), self.screen)
            pygame.display.update()
            
    def gameover_by_gravity(self):
        self.gui.sprite.first_frame = 2
        self.gui.sprite.last_frame = 3
        self.player.sprite.frame = 8
        
        while (self.dragon.X < 3500):
            self.dragon.X += 35
            framerate.tick(30)
            ticks = pygame.time.get_ticks()

            if self.player.Y < 1500:
                self.player.Y += 20

            self.player.update(0, 50)
            self.dragon.update(ticks, 150)
            self.gui.update(ticks, 600)

            self.render_scene()
            self.gui.draw(screen)
            pygame.display.update()
            
    def gameover_by_fire(self):
        store_y = self.player.Y
        store_time = pygame.time.get_ticks()
        self.gui.sprite.first_frame = 2
        self.gui.sprite.last_frame = 3
        self.scene.change_layer(self.player_sprite, 10)
        
        while (self.dragon.X < 3500):
            self.dragon.X += 35
            framerate.tick(30)
            ticks = pygame.time.get_ticks()
            seconds_since_death = (ticks - store_time) / 1000
            
            self.player.sprite.first_frame = 36
            self.player.sprite.last_frame = 43
            if self.player.Y < 1500:
                self.player.X += seconds_since_death * 6
                y_increase = 1428*math.pow(seconds_since_death, 2) - 1142*seconds_since_death
                self.player.Y = store_y + y_increase

            if self.player.sprite.frame == 43:
                self.player.sprite.first_frame = 42

            self.gui.first_frame = 2
            self.gui.last_frame = 3
            
            self.player.update(ticks, 50)
            self.dragon.update(ticks, 150)
            self.gui.update(ticks, 600)

            self.render_scene()
            self.gui.draw(screen)
            pygame.display.update()
            
    def gameover_by_barricade(self):
        self.gui.sprite.first_frame = 2
        self.gui.sprite.last_frame = 3
        self.player.sprite.frame = 8
        
        while (self.dragon.X < 3500):
            self.dragon.X += 35
            framerate.tick(30)
            ticks = pygame.time.get_ticks()

            if self.player.Y < 1500:
                self.player.Y += 20

            self.player.update(0, 50)
            self.dragon.update(ticks, 150)
            self.gui.update(ticks, 600)

            self.render_scene()
            self.gui.draw(screen)
            pygame.display.update()
            
     
    def render_scene(self):
        self.scene.draw(self.screen)
        
        
    def rand_start(self):
        self.l1 = [1,0,2,0,1,2,0,0,2,2]
        self.l2 = [1,1,2,2,0,2,0,1,2,1]
        self.current_random = self.l1
        self.inc = 0
    
        
    def next_rand(self):
        x = randint(1,100)
        if x < 20:
            if x > 10:
                self.current_random = self.l1
            else:
                self.current_random = self.l2
        c = self.current_random[self.inc]
        if self.inc > 8:
            self.inc = 0
        else:
            self.inc += 1
        return c
        
#main program begins
pygame.init()
screen = pygame.display.set_mode((1600,800))
pygame.display.set_caption("Dragon Escape Game")
font1 = pygame.font.Font(None, 36)
framerate = pygame.time.Clock()
main = MainGame(screen)


