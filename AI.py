import os
import random
import time
import neat
import pygame

pygame.font.init()
# setting up the resolution
HEIGHT = 800
WIDTH = 575
VELOCITY=5
# loading the images using pygame, scale2x doubles the size of image
BIRD_IMAGE = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird3.png"))),
]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "pipe.png")))
GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "base.png")))
BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 60)


# declaring the class   bird to control the character
class Bird:
    IMAGE = BIRD_IMAGE
    MAX_ROTATION = 25  # sets rotation of bird while moving up or down
    ROTATION_VELOCITY = 20  # how much will bird move wrt each frame
    ANIMATION_TIME = 5  # duration of animation of bird flapping its wings

    def __init__(self, x, y):
        # stating initial position of bird
        self.x = x
        self.y = y

        self.tilt = 0  # angle of the image ( to present an illustion of lift and fall)
        self.tick_count = 0

        self.velocity = 0
        self.height = self.y
        self.image_number = 0  # to count which image of bird we're in
        self.image = self.IMAGE[0]  # hold bird's image

    def jump(self):
        # in pygame, top left pixel is 0,0. So if we want to jump the bird up , we need to present negative value
        self.velocity = -10.5

        self.tick_count = 0  # take count of when we last jumped
        self.height = self.y

    def move(self):
        # function to be called every frame to move the bird
        self.tick_count += 1

        d = self.velocity * self.tick_count + 1.5 * (self.tick_count**2)
        # represents a physics equation of motion that govern the vertical motion of an object under the influence of gravity.
        # parabola of equation- y = ax + bx^2

        if d >= 16:  # terminal velocity
            d = 16
        if d < 0:
            d -= 2  # defines jump bosst, ie if it jumps x pixels, make it jump 2 pixels more

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            # d<0 means bird is moving upwards, or we can check by difference in value of initial and current height of bird
            if self.tilt < self.MAX_ROTATION:  # tilting the bird to a limit
                self.tilt = self.MAX_ROTATION
        else:
            # now when bird is not moving upwards, it'll be falling downwards
            if (self.tilt > -90):  # it decreases the value till it shows the bird nosediving
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        # calculalting which frame to show using animation time & frame number ( here mentioned as image_number )
        self.image_number += 1
        animation_frame = (self.image_number // self.ANIMATION_TIME % (2 * len(self.IMAGE) - 2))

        # it outputs image number of bird as 0,1,2,1,0... ( required for animation )
        if animation_frame < len(self.IMAGE):
            self.image = self.IMAGE[animation_frame]
        else:
            self.image = self.IMAGE[2 * len(self.IMAGE) - 2 - animation_frame]
        # above loop was used to set animation for bird ,by showing 1st frame to 2nd to 3rd,(rather than going directly to 1st frame,
        # looking odd animation) , we go from frame 2nd to 1st

        if self.tilt <= -80:
            self.image = self.IMAGE[1]
            self.image_number = self.ANIMATION_TIME * 2
            # when bird nosedive , it shouldn't flap it's bird, 2nd frame is used and then transferred to 3rd frame and cycles continues

        # rotating the image wrt angle, by default the image is rotated with it's top left pixel, changin it using get_rect
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.image.get_rect(topleft=(self.x, self.y)).center
        )

        window.blit(rotated_image, new_rect.topleft)
        # blit is used to combine or display images onto the game window- surface.blit(source, destination)

    # collision mask is a representation of the object's shape that is used for collision detection in games.
    # it takes the bird's image surface as input and generates a mask based on the non-transparent pixels of the image.
    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    GAP = 200
    
    def __init__(self, x):
        # setting the x axis value of pipe, as height with will random
        self.x = x
        self.height = 0

        # setting up location of top & bottom pipe
        self.top = 0
        self.bottom = 0

        # we need 2 pipes, one is upside down in y-axis, that is the reason of using flip
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False  # tells it bird already passed the pipe
        self.set_height()  # sets bottom & top height randomly

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        # by default pygame takes top left of image as it's origin, it'll work with bottom pipe ,
        # but we need to find the difference b/w height and height of image to find top of top pipe
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -=VELOCITY

    # presenting both pipes with their coordinates
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # getting mask for bird, top & bottom pipes
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # getting offsets of both pipes wrt bird
        top_pipe_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_pipe_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # finding collision points for bottom & top pipe
        bottom_collision_points = bird_mask.overlap(
            bottom_pipe_mask, bottom_pipe_offset
        )
        top_collision_points = bird_mask.overlap(top_pipe_mask, top_pipe_offset)

        # checking if any point overlapped with pipes, returns true if bird collided with pip
        if bottom_collision_points or top_collision_points:
            return True
        return False


class Base:
    WIDTH = GROUND_IMAGE.get_width()
    IMG = GROUND_IMAGE

    def __init__(self, y):
        # setting up 2 images of background in order to loop
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -=VELOCITY
        self.x2 -=VELOCITY

        # to check  the first ground image has moved completely off the screen to the left.
        if self.x1 + self.WIDTH < 0:
            # placing the first ground image just to the right of the second ground image.
            self.x1 = self.x2 + self.WIDTH

        # to check  the second ground image has moved completely off the screen to the left.
        if self.x2 + self.WIDTH < 0:
            # placing the second ground image just to the right of the first ground image.
            self.x2 = self.x1 + self.WIDTH

    def draw(self, windows):
        windows.blit(self.IMG, (self.x1, self.y))
        windows.blit(self.IMG, (self.x2, self.y))


# drawing the game window with all game objects
def draw_window(window, birds, pipes, base, score):
    window.blit(BACKGROUND, (0, 0))
    for pipe in pipes:
        pipe.draw(window)
    base.draw(window)
    for bird in birds:
        bird.draw(window)

    font_path = "flappy-bird-font.ttf"
    font_size = 75
    font = pygame.font.Font(font_path, font_size)
    font.set_bold(True)
    text = font.render(str(score), 1, (255, 255, 255))

    text_width = text.get_width()
    x_pos = WIDTH // 2 - text_width // 2
    window.blit(text, (x_pos, 100))

    pygame.display.update()


def main(genomes, config):
    nets = []
    ge = []
    birds = []
    
    global VELOCITY

    for _,g in genomes: #genomes is a tuple, with genome id and genome object
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    # setting starting position of all objects
    ground = Base(700)
    pipes = [Pipe(600)]

    score = 0  # setting up the score
    frame=0
    window = pygame.display.set_mode((WIDTH, HEIGHT))  # setting up the game window
    run = True  # setting this true till we want to continue the game
    clock = pygame.time.Clock()

    while run:
        clock.tick(30)  # setting the frame rate of game

        for (event) in (pygame.event.get()):  # used to retrieve a list of all the events that have occurred
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        frame+=1
        if(frame%150==0):
            frame=0
        VELOCITY=VELOCITY+VELOCITY*0.0005

        pipe_ind=0
        if len(birds)>0:
            if(len(pipes)>1 and  birds[0].x>pipes[0].x +pipes[0].PIPE_TOP.get_width()):
                #check if bird has passed the pipe , if so , pass the next pipe to the NN
                pipe_ind =1
            #for multiple pipes in the screen, to select which pipe to feed to the NN 
        else:
            run=False
            VELOCITY=5
            break #if no bird remain, we want new generation of birds 

        for x,bird in enumerate(birds):
            bird.move()
            ge[x].fitness+=0.1 #for surviving each second, we give bird fitness points, ie to incentivise bird to fly longer

            output=nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y-pipes[pipe_ind].bottom),VELOCITY))
            #uses the NN to control the bird, giving arguments as position of bird and front pipe
            if (output[0]>0.5):
                bird.jump() #if output of NN is above threshold, then only jump
        
        add_pipe = False
        rem = []#list to store pipes which needed to be removed
        for pipe in pipes:
            for x,bird in enumerate(birds):
                # using loop for each bird for it's collision
                if pipe.collide(bird):
                    # Handle bird collision with pipe
                    ge[x].fitness-=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x) #if a bird collides, we don't want to include that bird's info-it's genomes and NN

                if not pipe.passed and pipe.x < bird.x:
                    # Bird has passed the pipe
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                # Pipe has moved off the screen, add it to the removal list
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            # Increase the score and add a new pipe
            score += 1

            for g in ge:
                g.fitness+=5
            #we previously removed the defective birds, ie any bird that made this far gets points.
            pipes.append(Pipe(600))

        # Remove pipes that have moved off the screen
        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.image.get_height() > 730 or bird.y<=0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x) #if a bird falls, we don't want to include that bird's info-it's genomes and NN
        ground.move()

        draw_window(window, birds, pipes, ground, score)  # setting up the window with bird and background
    



# NEAT Algorithm Steps:

# 1. Population Initialization
#    - Create an initial population of neural networks with random structures and weights.

# 2. Evaluation
#    - Evaluate each neural network in the population on the task or problem.

# 3. Fitness Assignment
#    - Assign a fitness value to each neural network based on its performance.

# 4. Reproduction and Evolution
#    - Apply evolutionary operators (selection, crossover, and mutation) to generate the next generation.

#    - Crossover
#      - Combine the structures of two parent networks to create offspring with mixed traits.

#    - Mutation
#      - Apply random changes to the structure and weights of the offspring networks.

# 5. Speciation
#    - Group networks into species based on their structural similarity.

# 6. Iteration
#    - Repeat steps 2-5 for multiple generations to evolve and improve the neural networks.


def run(config_path):
    # function is responsible for running the NEAT algorithm using the provided configuration file.
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path,)
    # neat.config.Config object is created with it's arguments/ properties
    #it assumes we've set up NEAT argument by default

    p = neat.Population(config) #generate population using config file

    p.add_reporter(neat.StdOutReporter(True))
    # This reporter is responsible for printing information about the progress of the algorithm to the console.

    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # This reporter collects and reports statistical information about the evolution process.

    winner = p.run(main, 50)
    # determine the fitness of each bird based on fitness function/ which we defined as our main function


if __name__ == "__main__":
    #provides a way to distinguish between the script being run directly or imported as a module, 
    #allowing  control of the execution of certain code based on how the script is being used.


    # creating absolute file path to load our configuration file
    local_directory = os.path.dirname(__file__)
    config_path = os.path.join(local_directory, "Config.txt")
    run(config_path)
