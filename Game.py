import os 
import random
import time
import neat
import pygame

#setting up the resolution
HEIGHT=800
WIDTH=600

#loading the images using pygame, scale2x doubles the size of image
BIRD_IMAGE=[pygame.transform.scale2x(pygame.image.load(os.path.join("Images","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("Images","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("Images","bird3.png")))]
PIPE_IMAGE=pygame.transform.scale2x(pygame.image.load(os.path.join("Images","pipe.png")))
GROUND_IMAGE=pygame.transform.scale2x(pygame.image.load(os.path.join("Images","base.png")))
BACKGROUND=pygame.transform.scale2x(pygame.image.load(os.path.join("Images","bg.png")))

#declaring the class   bird to control the character
class Bird:
    IMAGE=BIRD_IMAGE
    MAX_ROTATION= 25            # sets rotation of bird while moving up or down
    ROTATION_VELOCITY=20        # how much will bird move wrt each frame
    ANIMATION_TIME=5        # duration of animation of bird flapping its wings

    def __init__(self,x,y) :
        #stating initial position of bird
        self.x=x
        self.y=y

        self.tilt=0 #angle of the image ( to present an illustion of lift and fall)
        self.tick_count=0
        
        self.velocity=0
        self.height=self.y
        self.image_number=0 #to count which image of bird we're in
        self.image=self.IMAGE[0] #hold bird's image
    
    def jump(self):
        
        #in pygame, top left pixel is 0,0. So if we want to jump the bird up , we need to present negative value
        self.velocity=-10.5 

        self.tick_count=0 #take count of when we last jumped
        self.height=self.y

    def move(self):
        self.tick_count+=1

        d=self.velocity * self.tick_count + 1.5 * (self.tick_count**2)
        # represents a physics equation of motion that govern the vertical motion of an object under the influence of gravity.

        if d>=16: #terminal velocity
            d=16
        if d<0: 
            d-=2

        self.y=self.y+d
        
        if d<0 or self.y < self.height+50:
            # d<0 means bird is moving upwards, or we can check by difference in value of initial and current height of bird
            if self.tilt<self.MAX_ROTATION:     #tilting th bird to a limit
                self.tilt=self.MAX_ROTATION
        else:
            #now when bird is not moving upwards, it'll be falling downwards
            if self.tilt>-90: #it decreases the value till it shows the bird nosediving
                self.tilt-=self.ROTATION_VELOCITY
    
    def draw (self, window):
        #selecting which frame of bird to present
        self.image_number+=1
        
        if self.image_number<self.ANIMATION_TIME:
            self.image=self.IMAGE[0]
        elif self.image_number<self.ANIMATION_TIME*2:
            self.image=self.IMAGE[1]
        elif self.image_number<self.ANIMATION_TIME*3:
            self.image=self.IMAGE[2]
        elif self.image_number<self.ANIMATION_TIME*4:
            self.image=self.IMAGE[1]
        elif self.image_number<self.ANIMATION_TIME*4+1:
            self.image=self.IMAGE[0]
            self.image_number=0

        '''
        above loop was used to set animation for bird ,by showing 1st frame to 2nd to 3rd,(rather than going directly to 1st frame, looking odd animation) , we go from frame 2nd to 1st 
        '''
            
        if self.tilt<=-80:
            self.image=self.IMAGE[1]
            self.image_number=self.ANIMATION_TIME*2
            #when bird nosedive , it shouldn't flap it's bird, 2nd frame is used and then transferred to 3rd frame and cycles continues

        #rotating the image wrt angle, by default the image is rotated with it's top left pixel, changin it using get_rect
        rotated_image=pygame.transform.rotate(self.image,self.tilt)
        new_rect=rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x,self.y)).center)

        window.blit(rotated_image,new_rect.topleft)
        #blit is used to combine or display images onto the game window

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

def draw_window(window,bird):
    window.blit(BACKGROUND,(0,0))
    bird.draw(window)
    pygame.display.update()

