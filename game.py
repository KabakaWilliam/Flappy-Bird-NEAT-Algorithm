import pygame
import neat
import time
import os
import random
pygame.font.init()
WinWidth = 500
WinHeight = 800
GEN = 0

BirdImgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
            ]

PipeImg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BaseImg =pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BgImg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

StatFont = pygame.font.SysFont("comicsans", 50)



class Bird:
    # constants
    IMGS = BirdImgs
    MaxRotation = 25 #as it goes up/down it will have to rotate
    RotVelocity = 20 #how much to rotate on each frame
    AnimationTime = 5 #how long to show bird animation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0 #tracks how many times moved since the last jump
        self.vel = 0
        self.height = self.y
        self.imgCount = 0 #counts how long an  image is  showing
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #0,0 in pygame is the top left. So moving up will be - velocity and down + velocity
        self.tickCount = 0
        self.height = self.y

    def move(self): #will call this method in the mainloop of the game so that things will move
        self.tickCount += 1

        #displacement. Calculates how many pixels up/down we are moving
        d = self.vel *self.tickCount + 1.5*self.tickCount ** 2

        if d >= 16: #downwards
            d = 16 #controls how fast we move down

        if d < 0: #upwards
            d -=2 #controls how fast we move up

        self.y = self.y + d

        if d < 0 or self.y < self.height +50: #second bit is to make the bird still face upwards as it falls
            if self.tilt < self.MaxRotation:
                self.tilt = self.MaxRotation
        else:
            if self.tilt > - 90: #face it downards. Rotate it to 90 degrees
                self.tilt -= self.RotVelocity

    def draw(self, win):
        # decides which image to show based on the current image count
        self.imgCount += 1

        if self.imgCount < self.AnimationTime:
            self.img = self.IMGS[0]
        elif self.imgCount < self.AnimationTime * 2:
            self.img = self.IMGS[1]
        elif self.imgCount < self.AnimationTime * 3:
            self.img = self.IMGS[2]
        elif self.imgCount < self.AnimationTime * 4:
            self.img = self.IMGS[1] #dont immediately skip to 0 because that would make the frames skip
        elif self.imgCount < self.AnimationTime * 4 + 1:
            self.img = self.IMGS[0]
            self.imgCount = 0

        if self.tilt <= -80: #If the bird is going down we want it not to flap
            self.img = self.IMGS[1]
            self.imgCount = self.AnimationTime * 2 #do this so that if we decide to jump
                                                #  it will not skip but will smoothly go to the 2nd image
            
        rotatedImage = pygame.transform.rotate(self.img, self.tilt)
        newRect = rotatedImage.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotatedImage, newRect.topleft)

    def getMask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0


        self.top = 0
        self.bottom = 0
        self.PipeTop = pygame.transform.flip(PipeImg, False, True)
        self.PipeBottom = PipeImg

        self.passed = False #checking if the bird has passed the pipe
        self.setHeight() #determine how tall the pipes will be

    def setHeight(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PipeTop.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win): #draw top and bottom
        win.blit(self.PipeTop, (self.x, self.top))
        win.blit(self.PipeBottom, (self.x, self.bottom))

    def collide(self, bird): #check if the pixels are overlapping
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.PipeTop)
        bottomMask = pygame.mask.from_surface(self.PipeBottom)

        topOffset = (self.x - bird.x, self.top - round(bird.y))  #offset from the bird to top mask of pipe
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        bPoint = birdMask.overlap(bottomMask, bottomOffset) #tells us the point of collisoon between
        # the bird mask and bottom pipe. If no collision, it returns none
        tPoint = birdMask.overlap(topMask, topOffset)

        if bPoint or tPoint:
            return True # if we collide with the pipe
        return False

class Base:
    VEL = 5 #Same speed as pipes movement
    WIDTH = BaseImg.get_width()
    IMG = BaseImg

    def __init__(self, y):
        self.y = y
        self.x1 = 0 #first image
        self.x2 = self.WIDTH #second image offscreen

    def move(self):
        self.x1 -=self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 +self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# draw background image and bird on top of it
# def drawWindow(win, bird, pipes, base, score):
#     win.blit(BgImg, (0, 0))  #top left image
#     for pipe in pipes:
#         pipe.draw(win)
#
#     text = StatFont.render("Score: " + str(score), 1, (255, 255, 255))
#     win.blit(text, (WinWidth - 10 - text.get_width(), 10))
#     base.draw(win)
#
#
#
#     bird.draw(win)
#     pygame.display.update() #updates display and refreshes it

def drawWindow(win, birds, pipes, base, score, gen):
    win.blit(BgImg, (0, 0))  # top left image
    for pipe in pipes:
        pipe.draw(win)

    text = StatFont.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WinWidth - 10 - text.get_width(), 10))

    text = StatFont.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)


    for bird in birds:
        bird.draw(win)

    pygame.display.update()  # updates display and refreshes it

# def main():
#     bird = Bird(230, 350)
#     base = Base (730)
#     pipes = [Pipe(700)] #will store pipes here
#     win = pygame.display.set_mode((WinWidth, WinHeight))
#     clock = pygame.time.Clock()
#
#     score = 0
#
#     run = True
#     while run:
#         clock.tick(30) #the loop should run for 30 ticks/ 30 frames per second
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#
#
#         # bird.move()
#         addPipe = False
#         rem = [] #store removed pipes
#         for pipe in pipes:
#             if pipe.collide(bird):
#                 pass
#             if pipe.x + pipe.PipeTop.get_width() < 0:
#                 rem.append(pipe)
#
#             if not pipe.passed and pipe.x < bird.x:
#                 pipe.passed = True
#                 addPipe = True
#
#             pipe.move()
#
#         if addPipe:
#             score += 1
#             pipes.append(Pipe(700)) # distance of pipes from each other
#
#         for r in rem:
#             pipes.remove(r)
#
#         if bird.y + bird.img.get_height() >= 730: #what to do if it touches the ground
#             pass
#
#         base.move()
#         drawWindow(win, bird, pipes, base, score)
#
#     pygame.quit()
#     quit()


# turn main into fitness function to work for all birds/genomes
def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes: #keep track of neural networks for a bird
        net = neat.nn.FeedForwardNetwork.create(g, config) #set up nn for genome
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g) #keep track of fitness in corespondance with the bird and nn

    base = Base(730)
    pipes = [Pipe(700)] #will store pipes here
    win = pygame.display.set_mode((WinWidth, WinHeight))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30) #the loop should run for 30 ticks/ 30 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()


        pipeInd = 0
        if len(birds) > 0: #make the birds  look at only one pipe
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PipeTop.get_width():
                pipeInd = 1 #if we pass one pipe, change the pipe we are looking at to the next in list

        else:
            run = False
            break

        for x, bird in enumerate(birds): #pass values to NN to get output to determine jump or not
            bird.move()
            ge[x].fitness += 0.1 #is a small amount of fitness because loop runs for 30fps

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeInd].height), abs(bird.y - pipes[pipeInd].bottom)))
    #         find distance from bird to top and bottom pipe
    # output will be a list of values. We have only one output neuron, but if you have more, youd want to specify
            if output[0] > 0.5:
                bird.jump()
    # bird.move()
        addPipe = False
        rem = [] #store removed pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird): #check if birds collide w pipe
                    ge[x].fitness -= 1 #each time a bird hits a pipe, it loses 1 frm fitness score
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                if not pipe.passed and pipe.x < bird.x: #check if bird has passed pipe
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.PipeTop.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700)) # distance of pipes from each other

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate (birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: #what to do if it touches the ground
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # score threshold
        # if score > 50:
        #     break

        base.move()
        drawWindow(win, birds, pipes, base, score, GEN)








def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                configPath)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # can add pickle here
    winner = p.run(main, 50) # Returns  best gene. we will run 50 generations. Call main 50 times and pass it the genomes of birds

    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    localDir = os.path.dirname(__file__) #give path to current directory
    configPath = os.path.join(localDir, "configBird.txt") #join local directory to name of config file
    run(configPath)



