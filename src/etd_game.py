'''
# Escape the Dragon Game
Created on 5 Jun 2016

@author: Fraser
'''

import sys, time, random, math, pygame
from pygame.locals import *

class MySprite(pygame.sprite.Sprite):
    def __init__(self, target):
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

    #X property
    def _getx(self): return self.rect.x
    def _setx(self, value): self.rect.x = value
    X = property(_getx,_setx)

    #Y property
    def _gety(self): return self.rect.y
    def _sety(self,value): self.rect.y = value
    Y = property(_gety,_sety)

    #position property
    def _getpos(self): return self.rect.topleft
    def _setpos(self, pos): self.rect.topleft = pos
    position = property(_getpos, _setpos)

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


def print_text(font, x, y, text, color=(255,255,255)):
    imgText = font.render(text, True, color)
    screen.blit(imgText, (x,y))
    
#main program begins
pygame.init()
screen = pygame.display.set_mode((1600,800))
pygame.display.set_caption("Escape The Stupid Dragon Game")
font1 = pygame.font.Font(None, 36)
framerate = pygame.time.Clock()

#create sprite groups
back_group = pygame.sprite.Group()
behind_player_group = pygame.sprite.Group()
mid_group = pygame.sprite.Group()
over_player_group = pygame.sprite.Group()
front_group = pygame.sprite.Group()
dragon_group = pygame.sprite.Group()
gui_group = pygame.sprite.Group()

sprite_groups = []
sprite_groups.append(back_group)
sprite_groups.append(behind_player_group)
sprite_groups.append(over_player_group)
sprite_groups.append(front_group)

#create background sprites

bg = MySprite(screen)
bg.load("../resources/backdrop.png", 1600, 800, 1)
bg.position = 0,0
back_group.add(bg)
bg2 = MySprite(screen)
bg2.load("../resources/backdrop.png", 1600, 800, 1)
bg2.position = 1600,0
back_group.add(bg2)

front_wall = MySprite(screen)
front_wall.load("../resources/front_wall.png", 1600, 800, 1)
bg.position = 0,0
front_group.add(front_wall)
front_wall2 = MySprite(screen)
front_wall2.load("../resources/front_wall.png", 1600, 800, 1)
front_wall2.position = 1600,0
front_group.add(front_wall2)

#create the dragon sprite
dragon = MySprite(screen)
dragon.load("../resources/dragon_sprite_sheet.png", 600, 332, 4 )
dragon.position = -808, 80
dragon_group.add(dragon)

#create the player sprite
player = MySprite(screen)
player.load("../resources/geoff_sprite_sheet.png", 256, 256, 8)
player.first_frame = 0
player.last_frame = 7
player.position = 675, 340
mid_group.add(player)

#create pit sprite
pit = MySprite(screen)
pit.load("../resources/jump_gap.png", 512, 512, 1)
pit.position = -1000, 195
behind_player_group.add(pit)

#create torch obstacle
torch = MySprite(screen)
torch.load("../resources/torch_hurdle.png", 512, 512, 9)
torch.position = -1000, 170
over_player_group.add(torch)

#create torch back wall
torch_back = MySprite(screen)
torch_back.load("../resources/torch_hurdle_back.png", 512, 512, 1)
torch_back.position = -1000, 170
behind_player_group.add(torch_back)

# create barricade
barricade = MySprite(screen)
barricade.load("../resources/barricade_sprite_sheet.png", 512, 512, 4)
barricade.position = -1000, 118
barricade.first_frame = 0
barricade.last_frame = 0
behind_player_group.add(barricade)

# create the gui sprite
gui = MySprite(screen)
gui.load("../resources/gui.png", 946, 205, 4)
gui.position = 800 - (gui.frame_width / 2), 150
gui.first_frame = 0
gui.last_frame = 1
gui_group.add(gui)



game_over = 0
game_started = False
player_jumping = False
player_sliding = False
player_punching = False
jump_vel = 0.0
player_start_y = player.Y
game_speed = 25
jumped = False
end_of_slide = False
jump_height = 1.5
last_speed_change = 0
score = 0
barricade_broken = False

#repeating loop
while True:
    while not game_started:
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
            player_jumping = False
            player_sliding = False
            player_punching = False
            game_started = True

        for s in back_group:
            s.X -= game_speed
        for i in front_group:
            i.X -= game_speed

        if bg.X < -1600:
            bg.X += 3200
        if bg2.X < -1600:
            bg2.X += 3200
        if front_wall.X < -1600:
            front_wall.X += 3200
        if front_wall2.X < -1600:
            front_wall2.X += 3200

        gui.first_frame = 0
        gui.last_frame = 1
        
        #update sprites
        back_group.update(ticks, 50)
        mid_group.update(ticks, 50)
        front_group.update(ticks, 50)
        gui_group.update(ticks, 400)

            
        # draw the stuff
        back_group.draw(screen)
        mid_group.draw(screen)
        front_group.draw(screen)
        gui_group.draw(screen)
        
        pygame.display.update()

        
    while not game_over:
        framerate.tick(30)
        ticks = pygame.time.get_ticks()
        score += 0.05
        
        if abs(ticks - last_speed_change) > 2000:
            last_speed_change = ticks
            game_speed += 1
            if game_speed > 40:
                game_speed = 40

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
            if not player_jumping and not player_sliding and not player_punching:
                player_jumping = True
                player.first_frame = 8
                player.last_frame = 15
                player.frame = 8
                jump_time = ticks
        elif keys[K_s]:
            if not player_jumping and not player_sliding and not player_punching:
                player_sliding = True
                player.first_frame = 16
                player.last_frame = 35
                player.frame = 16
        elif keys[K_d]:
            if not player_jumping and not player_sliding and not player_punching:
                player_punching = True
                player.first_frame = 44
                player.last_frame = 51
                player.frame = 44

        # move sprites
        for grp in sprite_groups:   
            for sp in grp.sprites():
                sp.X -= game_speed

        if dragon.X < 4:
            dragon.X += 10
            if dragon.X > 4:
                dragon.X = 4

        if bg.X < -1600:
            bg.X += 3200
        if bg2.X < -1600:
            bg2.X += 3200
        if front_wall.X < -1600:
            front_wall.X += 3200
        if front_wall2.X < -1600:
            front_wall2.X += 3200

        if pit.X < -520 and torch.X < -520 and barricade.X < -520:
            num = random.randint(0,2)
            if num == 0:
                pit.X = random.randint(1605, 1750)
            else:
                if num == 1:
                    new_x = random.randint(1605, 1850)
                    torch.X = new_x
                    torch_back.X = new_x
                else:
                    barricade.X = random.randint(1605, 1750)
                    barricade.first_frame = 0
                    barricade.last_frame = 0
                    barricade_broken = False
                    
    

        # player jump
        if player_jumping:
            jump_vel = 0.6*math.pow((player.frame - 11.5), 3) * jump_height
            if jumped and player.frame == 8:
                jumped = False
                jump_vel = 0
                player.first_frame = 0
                player.last_frame = 7
                player.frame = 0
                player.Y = player_start_y
                player_jumping = False
            if player.frame == 15:
                jumped = True
                

        
        player.Y += jump_vel

        # player slide
        if player_sliding:
            if end_of_slide and player.frame == 16:
                end_of_slide = False
                player.first_frame = 0
                player.last_frame = 7
                player.frame = 0
                player_sliding = False
            if player.frame == 35:
                end_of_slide = True
                
        # plyer_punch
        if player_punching and player.frame == 51:
            player.first_frame = 0
            player.last_frame = 7
            player_punching = False

        if pygame.sprite.collide_circle(pit, player) and not player_jumping:
            player.X = pit.X + pit.frame_width/4
            game_over = 1
            
        if pygame.sprite.collide_circle(torch, player) and not player_sliding:
            game_over = 2
            store_time = ticks
            store_y = player.Y

        if pygame.sprite.collide_circle(barricade, player):
            if player_punching:
                barricade_broken = True
                barricade.first_frame = 0
                barricade.last_frame = 7
            else:
                if not barricade_broken:
                    game_over = 1
                
        if barricade_broken:
                if barricade.frame == 7:
                    barricade.first_frame = 7
                    barricade.last_frame = 7
        
        #update sprites
        if not game_over:
            back_group.update(ticks, 50)
            behind_player_group.update(ticks, 35)
            if player_jumping:
                mid_group.update(ticks, 100*(25/game_speed))
            elif player_sliding:
                mid_group.update(ticks, 45*(25/game_speed))
            else:
                mid_group.update(ticks, 50)
            over_player_group.update(ticks, 50)
            front_group.update(ticks, 50)
            dragon_group.update(ticks, 150)
            
        # draw the stuff
        back_group.draw(screen)
        behind_player_group.draw(screen)
        mid_group.draw(screen)
        over_player_group.draw(screen)
        front_group.draw(screen)
        dragon_group.draw(screen)
        print_text(font1, 1400, 20, "Score: ")
        print_text(font1, 1500, 20, str(int(score*game_speed)))
        
        pygame.display.update()
        
    if game_over == 1:
        
        framerate.tick(30)
        ticks = pygame.time.get_ticks()
        
        player.frame = 8
        
        if dragon.X < 2500:
            dragon.X += 35
        if player.Y < 1500:
            player.Y += 20

        gui.first_frame = 2
        gui.last_frame = 3
        
        back_group.update(ticks, 50)
        behind_player_group.update(ticks, 35)
        mid_group.update(0, 50)
        over_player_group.update(ticks, 50)
        front_group.update(ticks, 50)
        dragon_group.update(ticks, 150)
        gui_group.update(ticks, 600)

        
        #draw everything
        back_group.draw(screen)
        behind_player_group.draw(screen)
        mid_group.draw(screen)
        over_player_group.draw(screen)
        front_group.draw(screen)
        dragon_group.draw(screen)
        gui_group.draw(screen)

        pygame.display.update()

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
        if keys[K_RETURN]:
            game_over = 0
            game_started = False
            dragon.position = -808, 80
            player.position = 675, 340
            score = 0
            game_speed = 25
            pit.position = -1000, 195
            torch.position = -1000, 170
            torch_back.position = -1000, 170
            player.first_frame = 0
            player.last_frame = 7
            player.frame = 0
            gui.frame = 0
        
    else:
        framerate.tick(30)
        ticks = pygame.time.get_ticks()
        seconds_since_death = (ticks - store_time) / 1000
        
        player.first_frame = 36
        player.last_frame = 43
        if player.Y < 1500:
            player.X += seconds_since_death * 6
            y_increase = 1428*math.pow(seconds_since_death, 2) - 1142*seconds_since_death
            player.Y = store_y + y_increase

        if dragon.X < 2500:
            dragon.X += 35
        
        if player.frame == 43:
            player.first_frame = 42

        gui.first_frame = 2
        gui.last_frame = 3
        
        back_group.update(ticks, 50)
        behind_player_group.update(ticks, 35)
        mid_group.update(ticks, 50)
        over_player_group.update(ticks, 50)
        front_group.update(ticks, 50)
        dragon_group.update(ticks, 150)
        gui_group.update(ticks, 600)
        
        #draw everything
        back_group.draw(screen)
        behind_player_group.draw(screen)
        
        over_player_group.draw(screen)
        front_group.draw(screen)
        dragon_group.draw(screen)
        mid_group.draw(screen)
        gui_group.draw(screen)
        
        pygame.display.update()

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
        if keys[K_RETURN]:
            game_over = 0
            game_started = False
            dragon.position = -808, 80
            player.position = 675, 340
            score = 0
            game_speed = 25
            pit.position = -1000, 195
            torch.position = -1000, 170
            torch_back.position = -1000, 170
            player.first_frame = 0
            player.last_frame = 7
            player.frame = 0
            gui.frame = 0





